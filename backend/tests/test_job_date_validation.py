import pytest
from datetime import datetime, timedelta
from app.services.job_date_validation_service import (
    job_date_validation_service,
    JobDateValidationService,
    JobDateCache
)
from app.integrations.serpapi.client import serpapi_client


def test_job_date_cache_operations():
    cache = JobDateCache(default_ttl_seconds=2)
    cache.set("test_key", {"title": "Software Engineer"})
    
    # Hit
    cached = cache.get("test_key")
    assert cached is not None
    assert cached["title"] == "Software Engineer"

    # Miss
    assert cache.get("non_existent_key") is None

    # Clear
    cache.clear()
    assert cache.get("test_key") is None


def test_date_parsing_relative_and_absolute():
    ref_time = datetime(2026, 9, 26, 12, 0, 0)

    # 1. Fresh relative dates
    dt_today, _ = JobDateValidationService.parse_relative_or_absolute_date("today", reference_time=ref_time)
    assert dt_today.date() == ref_time.date()

    dt_yesterday, _ = JobDateValidationService.parse_relative_or_absolute_date("yesterday", reference_time=ref_time)
    assert (ref_time - dt_yesterday).days == 1

    dt_3days, _ = JobDateValidationService.parse_relative_or_absolute_date("3 days ago", reference_time=ref_time)
    assert (ref_time - dt_3days).days == 3

    dt_2weeks, _ = JobDateValidationService.parse_relative_or_absolute_date("2 weeks ago", reference_time=ref_time)
    assert (ref_time - dt_2weeks).days == 14

    dt_1month, _ = JobDateValidationService.parse_relative_or_absolute_date("1 month ago", reference_time=ref_time)
    assert 28 <= (ref_time - dt_1month).days <= 31

    # 2. Stale / Old relative dates (> 60 days / 2-3 years ago)
    dt_3months, _ = JobDateValidationService.parse_relative_or_absolute_date("3 months ago", reference_time=ref_time)
    assert (ref_time - dt_3months).days >= 85

    dt_1year, _ = JobDateValidationService.parse_relative_or_absolute_date("1 year ago", reference_time=ref_time)
    assert (ref_time - dt_1year).days >= 360

    dt_2years, _ = JobDateValidationService.parse_relative_or_absolute_date("2 years ago", reference_time=ref_time)
    assert (ref_time - dt_2years).days >= 700

    dt_3years, _ = JobDateValidationService.parse_relative_or_absolute_date("3 years ago", reference_time=ref_time)
    assert (ref_time - dt_3years).days >= 1000

    # 3. Absolute ISO dates
    dt_iso, _ = JobDateValidationService.parse_relative_or_absolute_date("2026-09-20T10:00:00", reference_time=ref_time)
    assert dt_iso == datetime(2026, 9, 20, 10, 0, 0)


def test_validate_job_recency_60_days():
    ref_time = datetime(2026, 9, 26, 12, 0, 0)

    # Valid fresh jobs (posted within 60 days)
    fresh_jobs = [
        {"title": "Dev 1", "posted_at": "2 days ago"},
        {"title": "Dev 2", "detected_extensions": {"posted_at": "1 week ago"}},
        {"title": "Dev 3", "extensions": ["3 weeks ago", "Full-time"]},
        {"title": "Dev 4", "posted_at": "1 month ago"},
        {"title": "Dev 5", "posted_at": "2 months ago"},
        {"title": "Dev 6", "posted_at": "2026-09-01"},
    ]

    for job in fresh_jobs:
        is_valid, dt, reason = JobDateValidationService.validate_job_recency(job, max_days=60, reference_time=ref_time)
        assert is_valid is True, f"Expected {job} to be valid, but got: {reason}"

    # Stale jobs (posted > 60 days / 2-3 years ago)
    stale_jobs = [
        {"title": "Old Dev 1", "posted_at": "3 months ago"},
        {"title": "Old Dev 2", "detected_extensions": {"posted_at": "6 months ago"}},
        {"title": "Old Dev 3", "extensions": ["1 year ago", "Full-time"]},
        {"title": "Old Dev 4", "posted_at": "2 years ago"},
        {"title": "Old Dev 5", "posted_at": "3 years ago"},
        {"title": "Old Dev 6", "posted_at": "2023-05-12T00:00:00"},
        {"title": "Old Dev 7", "posted_at": "2024-01-15"},
    ]

    for job in stale_jobs:
        is_valid, dt, reason = JobDateValidationService.validate_job_recency(job, max_days=60, reference_time=ref_time)
        assert is_valid is False, f"Expected {job} to be rejected, but it was marked valid!"
        assert ("exceeds" in reason or "rejected" in reason or "ago" in reason)


def test_filter_and_validate_job_list():
    raw_job_pool = [
        {"job_id": "j1", "title": "React Engineer", "posted_at": "1 day ago"},
        {"job_id": "j2", "title": "Stale Angular Dev", "posted_at": "3 years ago"},
        {"job_id": "j3", "title": "Full Stack Dev", "detected_extensions": {"posted_at": "2 weeks ago"}},
        {"job_id": "j4", "title": "Stale Java Dev", "extensions": ["2 years ago", "Contract"]},
        {"job_id": "j5", "title": "Python Developer", "posted_at": "2026-09-24T10:00:00"},
        {"job_id": "j6", "title": "Old Node Dev", "posted_at": "4 months ago"}
    ]

    filtered = job_date_validation_service.filter_and_validate_job_list(raw_job_pool, max_days=60)
    
    # Must only retain j1, j3, j5
    assert len(filtered) == 3
    valid_ids = {j["job_id"] for j in filtered}
    assert valid_ids == {"j1", "j3", "j5"}
    assert "j2" not in valid_ids
    assert "j4" not in valid_ids
    assert "j6" not in valid_ids


@pytest.mark.asyncio
async def test_serpapi_client_enforces_date_validation():
    # SerpApi client should always return jobs within the 60-day window
    results = await serpapi_client.search_google_jobs(query="Full Stack Developer", location="Ahmedabad")
    assert len(results) > 0

    for job in results:
        is_valid, dt, reason = JobDateValidationService.validate_job_recency(job, max_days=60)
        assert is_valid is True, f"SerpApi returned a stale job: {job.get('title')} ({reason})"
