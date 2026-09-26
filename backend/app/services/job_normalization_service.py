import re
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.job_date_validation_service import job_date_validation_service


class JobNormalizationService:
    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        if not text:
            return ""
        # Strip HTML tags
        cleaned = re.sub(r"<[^>]*>", " ", text)
        # Normalize whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    @classmethod
    def parse_datetime(cls, val: Any) -> datetime:
        if isinstance(val, datetime):
            return val
        if isinstance(val, str) and val.strip():
            dt, _ = job_date_validation_service.parse_relative_or_absolute_date(val)
            if dt:
                return dt
        return datetime.utcnow()

    @classmethod
    def normalize_job(cls, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        title = cls.clean_text(raw_job.get("title", "Software Developer"))
        company_name = cls.clean_text(raw_job.get("company_name", "Technology Employer"))
        location = cls.clean_text(raw_job.get("location", "Remote"))
        description = cls.clean_text(raw_job.get("description", ""))
        
        # Extract posted date string if not directly passed
        posted_at_raw = raw_job.get("posted_at") or job_date_validation_service.extract_raw_posted_string(raw_job)
        
        return {
            "provider": raw_job.get("provider", "serpapi_google_jobs"),
            "provider_job_id": raw_job.get("job_id"),
            "title": title,
            "normalized_title": title.lower(),
            "company_name": company_name,
            "location": location,
            "remote_type": "remote" if "remote" in location.lower() or "remote" in title.lower() else "onsite",
            "description": description,
            "apply_url": raw_job.get("apply_url"),
            "source_url": raw_job.get("source_url"),
            "posted_at": cls.parse_datetime(posted_at_raw),
            "raw_payload": raw_job.get("raw_payload", {})
        }


job_normalization_service = JobNormalizationService()
