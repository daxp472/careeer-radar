import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.logging import logger


class JobDateCache:
    """
    In-memory date and query cache with TTL to store validated job results
    and prevent re-fetching stale jobs or repeating expensive parsing.
    """
    def __init__(self, default_ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None
        return entry["data"]

    def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl,
            "created_at": time.time()
        }

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        now = time.time()
        # Clean expired
        expired = [k for k, v in self._cache.items() if now > v["expires_at"]]
        for k in expired:
            del self._cache[k]
        return len(self._cache)


class JobDateValidationService:
    """
    Service to parse, validate, and enforce date freshness for jobs fetched via SerpApi
    or queried from the central job database.
    Strictly filters out jobs posted more than 60 days ago (or > 2 months ago, e.g. 2-3 years ago).
    """

    MAX_RECENCY_DAYS = 60  # Current month + previous month (maximum 2 months / 60 days)

    def __init__(self):
        self.cache = JobDateCache(default_ttl_seconds=settings.SEARCH_CACHE_HOURS_TTL * 3600)

    @classmethod
    def extract_raw_posted_string(cls, raw_job: Dict[str, Any]) -> Optional[str]:
        """
        Extract the posted date string from any known Google Jobs / SerpApi field.
        """
        # 1. Direct posted_at field
        if raw_job.get("posted_at"):
            val = raw_job["posted_at"]
            if isinstance(val, str) and val.strip():
                return val.strip()

        # 2. detected_extensions -> posted_at
        detected = raw_job.get("detected_extensions") or {}
        if isinstance(detected, dict) and detected.get("posted_at"):
            val = detected["posted_at"]
            if isinstance(val, str) and val.strip():
                return val.strip()

        # 3. Check inside extensions list
        extensions = raw_job.get("extensions") or []
        if isinstance(extensions, list):
            for ext in extensions:
                if isinstance(ext, str):
                    ext_clean = ext.strip().lower()
                    if any(kw in ext_clean for kw in ["ago", "yesterday", "today", "just now", "posted", "day", "month", "year", "week", "hour"]):
                        return ext.strip()

        # 4. Check inside raw_payload if nested
        payload = raw_job.get("raw_payload") or {}
        if isinstance(payload, dict):
            p_detected = payload.get("detected_extensions") or {}
            if isinstance(p_detected, dict) and p_detected.get("posted_at"):
                return str(p_detected["posted_at"]).strip()
            p_ext = payload.get("extensions") or []
            if isinstance(p_ext, list):
                for ext in p_ext:
                    if isinstance(ext, str) and any(kw in ext.lower() for kw in ["ago", "yesterday", "today", "posted", "day", "month", "year", "week"]):
                        return ext.strip()

        return None

    @classmethod
    def parse_relative_or_absolute_date(cls, date_str: Optional[str], reference_time: Optional[datetime] = None) -> Tuple[Optional[datetime], Optional[str]]:
        """
        Parse relative ("3 days ago", "1 month ago", "2 years ago") or absolute dates ("2026-09-24")
        into a datetime and normalized raw text.
        """
        if not date_str:
            return None, None

        ref = reference_time or datetime.utcnow()
        clean = date_str.strip()
        lower = clean.lower()

        # 1. Immediate keywords
        if "just now" in lower or "today" in lower:
            return ref, clean
        if "yesterday" in lower:
            return ref - timedelta(days=1), clean

        # 2. Regex for relative time: "X hours ago", "X days ago", "X weeks ago", "X months ago", "X years ago"
        relative_match = re.search(r"(\d+)\s*\+?\s*(minute|hour|day|week|month|year)s?\s+ago", lower)
        if relative_match:
            amount = int(relative_match.group(1))
            unit = relative_match.group(2)

            if unit == "minute":
                return ref - timedelta(minutes=amount), clean
            elif unit == "hour":
                return ref - timedelta(hours=amount), clean
            elif unit == "day":
                return ref - timedelta(days=amount), clean
            elif unit == "week":
                return ref - timedelta(days=amount * 7), clean
            elif unit == "month":
                # Approximate 1 month = 30 days
                return ref - timedelta(days=amount * 30), clean
            elif unit == "year":
                # Approximate 1 year = 365 days
                return ref - timedelta(days=amount * 365), clean

        # 3. Handle phrases like "a month ago", "a year ago", "a week ago", "a day ago"
        if "a month ago" in lower or "1 month ago" in lower:
            return ref - timedelta(days=30), clean
        if "2 months ago" in lower:
            return ref - timedelta(days=60), clean
        if "a year ago" in lower or "1 year ago" in lower:
            return ref - timedelta(days=365), clean
        if "a week ago" in lower:
            return ref - timedelta(days=7), clean
        if "a day ago" in lower:
            return ref - timedelta(days=1), clean

        # 4. Try standard ISO / datetime formats
        for fmt in (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%Y/%m/%d"
        ):
            try:
                # Remove timezone offset strings like +00:00 or Z for simple parsing
                sanitized = re.sub(r"([+-]\d\d:\d\d|Z)$", "", clean)
                dt = datetime.strptime(sanitized, fmt)
                return dt, clean
            except ValueError:
                continue

        # 5. Check if string contains an old year (e.g. 2021, 2022, 2023, 2024 when ref is 2026)
        year_match = re.search(r"\b(201\d|202[0-4])\b", clean)
        if year_match:
            old_year = int(year_match.group(1))
            if ref.year - old_year >= 1:
                # Far in the past
                return datetime(old_year, 1, 1), clean

        return None, clean

    @classmethod
    def validate_job_recency(
        cls,
        raw_job: Dict[str, Any],
        max_days: int = MAX_RECENCY_DAYS,
        reference_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[datetime], str]:
        """
        Validate whether a job is fresh (within max_days, default 60 days / 2 months).
        Returns: (is_fresh, parsed_datetime, explanation)
        """
        ref = reference_time or datetime.utcnow()
        cutoff_date = ref - timedelta(days=max_days)

        raw_date_str = cls.extract_raw_posted_string(raw_job)
        parsed_dt, raw_text = cls.parse_relative_or_absolute_date(raw_date_str, reference_time=ref)

        # Explicit check for keywords denoting jobs older than 2 months
        if raw_text:
            lower_text = raw_text.lower()
            # If text indicates years ago (e.g., "1 year ago", "2 years ago", "3 years ago")
            if re.search(r"\b(\d+)\s*\+?\s*years?\s+ago\b", lower_text) or "a year ago" in lower_text:
                return False, parsed_dt, f"Job rejected: posted '{raw_text}' (exceeds {max_days}-day recency limit)."

            # If text indicates 3 or more months ago (e.g., "3 months ago", "5 months ago")
            month_match = re.search(r"\b(\d+)\s*\+?\s*months?\s+ago\b", lower_text)
            if month_match:
                months = int(month_match.group(1))
                if months > 2:
                    return False, parsed_dt, f"Job rejected: posted '{raw_text}' (>2 months old, exceeds limit)."

        # If we successfully parsed a datetime, enforce the cutoff
        if parsed_dt:
            if parsed_dt < cutoff_date:
                days_old = (ref - parsed_dt).days
                return False, parsed_dt, f"Job rejected: posted on {parsed_dt.strftime('%Y-%m-%d')} ({days_old} days ago > {max_days} days)."
            return True, parsed_dt, f"Job valid: posted on {parsed_dt.strftime('%Y-%m-%d')} within {max_days}-day window."

        # If no explicit date string was present in raw_job:
        # In Google Jobs with 'date_posted:month' chips, fresh query results without explicit date are accepted as current
        # but stamped with the current timestamp.
        return True, ref, "Job valid: fresh search query result (stamped with current timestamp)."

    @classmethod
    def filter_and_validate_job_list(
        cls,
        raw_jobs: List[Dict[str, Any]],
        max_days: int = MAX_RECENCY_DAYS
    ) -> List[Dict[str, Any]]:
        """
        Filter a list of raw job dicts, keeping only jobs posted within max_days (<= 60 days).
        Attaches the parsed datetime as 'posted_at'.
        """
        valid_jobs = []
        filtered_count = 0

        for rj in raw_jobs:
            is_valid, parsed_dt, reason = cls.validate_job_recency(rj, max_days=max_days)
            if is_valid:
                # Ensure posted_at is standardized
                rj_copy = dict(rj)
                rj_copy["posted_at"] = parsed_dt.isoformat() if parsed_dt else datetime.utcnow().isoformat()
                valid_jobs.append(rj_copy)
            else:
                filtered_count += 1
                job_title = rj.get("title", "Unknown Job")
                company = rj.get("company_name", "Unknown Company")
                logger.info(f"[JobDateValidation] Filtered out stale job '{job_title}' at '{company}': {reason}")

        logger.info(f"[JobDateValidation] Evaluated {len(raw_jobs)} jobs -> {len(valid_jobs)} valid recent jobs, {filtered_count} stale listings filtered out.")
        return valid_jobs


job_date_validation_service = JobDateValidationService()
