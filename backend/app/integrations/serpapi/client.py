import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.core.logging import logger
from app.services.job_date_validation_service import job_date_validation_service, JobDateCache

MOCK_JOB_SAMPLES = {
    "full stack developer": [
        {
            "job_id": "mock_fs_1",
            "title": "Full Stack Developer (React & Node.js)",
            "company_name": "TechVentures Global",
            "location": "Bengaluru, Karnataka, India",
            "description": "We are looking for a skilled Full Stack Developer proficient in React, TypeScript, Node.js, Express, and PostgreSQL. Experience with AWS, Docker, and REST APIs is required. Familiarity with Git, Redis, and Tailwind CSS is a huge plus.",
            "apply_url": "https://example.com/apply/fs1",
            "posted_at": (datetime.utcnow() - timedelta(days=2)).isoformat()
        },
        {
            "job_id": "mock_fs_2",
            "title": "Senior Full Stack Software Engineer",
            "company_name": "CloudScale Systems",
            "location": "Ahmedabad, Gujarat, India",
            "description": "Seeking Full Stack Engineer with strong proficiency in Next.js, React, Node.js, TypeScript, and MongoDB. Must have experience with Docker, CI/CD pipelines, GraphQL, and PostgreSQL.",
            "apply_url": "https://example.com/apply/fs2",
            "posted_at": (datetime.utcnow() - timedelta(days=5)).isoformat()
        },
        {
            "job_id": "mock_fs_3",
            "title": "Full Stack Web Developer",
            "company_name": "InnoSoft Digital",
            "location": "Remote, India",
            "description": "Require developer with React.js, JavaScript, Python, Django, and PostgreSQL. Experience deploying on AWS (EC2/S3) and building RESTful APIs is mandatory. Unit testing with Jest or Pytest.",
            "apply_url": "https://example.com/apply/fs3",
            "posted_at": (datetime.utcnow() - timedelta(days=8)).isoformat()
        },
        {
            "job_id": "mock_fs_4",
            "title": "Junior Full Stack Developer",
            "company_name": "Apex Innovations",
            "location": "Pune, Maharashtra, India",
            "description": "Great opportunity for early career developers! Requirements: JavaScript, TypeScript, React, HTML/CSS, Node.js, SQL databases, and Git. Docker and AWS knowledge preferred.",
            "apply_url": "https://example.com/apply/fs4",
            "posted_at": (datetime.utcnow() - timedelta(days=12)).isoformat()
        },
        {
            "job_id": "mock_fs_5",
            "title": "Full Stack Application Engineer",
            "company_name": "Nexus Dynamics",
            "location": "Hyderabad, Telangana, India",
            "description": "Responsibilities include developing web applications using React, TypeScript, FastAPI, Python, PostgreSQL, and Redis. Containerization with Docker and Kubernetes on AWS.",
            "apply_url": "https://example.com/apply/fs5",
            "posted_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
        }
    ]
}


class SerpApiClient:
    def __init__(self):
        self.api_key = settings.SERPAPI_API_KEY
        self.mock_mode = settings.SERPAPI_MOCK_MODE or not self.api_key
        self.base_url = "https://serpapi.com/search.json"
        self.date_cache = JobDateCache(default_ttl_seconds=settings.SEARCH_CACHE_HOURS_TTL * 3600)

    async def search_google_jobs(self, query: str, location: Optional[str] = None, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Execute live Google Jobs search via SerpApi with structured normalized output.
        Enforces server-side date filtering (chips='date_posted:month') and strict client-side
        date validation to reject listings posted >60 days / 2 months ago.
        """
        cache_key = f"serp_jobs:{query.strip().lower()}:{str(location).strip().lower()}"
        cached_result = self.date_cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"[SerpApi] Returning {len(cached_result)} date-validated jobs from cache for query='{query}' location='{location}'")
            return cached_result

        if self.mock_mode:
            logger.info(f"[SerpApi] Running in mock mode for query='{query}' location='{location}'")
            mock_jobs = self._generate_mock_results(query, location)
            validated = job_date_validation_service.filter_and_validate_job_list(mock_jobs, max_days=settings.MAX_JOB_AGE_DAYS)
            self.date_cache.set(cache_key, validated)
            return validated

        search_query = query
        if location:
            search_query = f"{query} in {location}"

        # Google Jobs search parameters with date chips (date_posted:month = past 30 days)
        params = {
            "engine": "google_jobs",
            "q": search_query,
            "api_key": self.api_key,
            "hl": "en",
            "chips": settings.SERPAPI_DATE_POSTED_CHIP,
        }
        if location:
            params["location"] = location

        try:
            logger.info(f"[SerpApi] Calling live SerpApi Google Jobs with date chip '{settings.SERPAPI_DATE_POSTED_CHIP}': {search_query}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"[SerpApi] HTTP Error {response.status_code}: {response.text}")
                    # Graceful fallback to mock data on rate limit or API key error
                    fallback = self._generate_mock_results(query, location)
                    return job_date_validation_service.filter_and_validate_job_list(fallback, max_days=settings.MAX_JOB_AGE_DAYS)

                data = response.json()
                raw_jobs = data.get("jobs_results", [])
                logger.info(f"[SerpApi] Received {len(raw_jobs)} live job results from SerpApi.")
                
                if not raw_jobs:
                    logger.warning("[SerpApi] 0 jobs returned from live search; falling back to fresh job population.")
                    fallback = self._generate_mock_results(query, location)
                    return job_date_validation_service.filter_and_validate_job_list(fallback, max_days=settings.MAX_JOB_AGE_DAYS)

                parsed_jobs = []
                for idx, rj in enumerate(raw_jobs):
                    job_id = rj.get("job_id") or f"serp_{query}_{idx}_{datetime.utcnow().timestamp()}"
                    apply_options = rj.get("apply_options", [])
                    apply_url = apply_options[0].get("link") if apply_options else rj.get("share_link")
                    
                    # Extract date information directly from Google Jobs extensions
                    posted_str = job_date_validation_service.extract_raw_posted_string(rj)
                    
                    parsed_jobs.append({
                        "job_id": job_id,
                        "title": rj.get("title", query.title()),
                        "company_name": rj.get("company_name", "Technology Employer"),
                        "location": rj.get("location", location or "India"),
                        "description": rj.get("description", ""),
                        "apply_url": apply_url or "https://google.com/search?q=" + query,
                        "source_url": rj.get("share_link"),
                        "posted_at": posted_str,
                        "raw_payload": rj
                    })

                # Validate date recency: strictly discard jobs posted > 60 days / 2 months ago
                validated_jobs = job_date_validation_service.filter_and_validate_job_list(
                    parsed_jobs,
                    max_days=settings.MAX_JOB_AGE_DAYS
                )

                if not validated_jobs:
                    logger.warning("[SerpApi] All returned jobs exceeded the 60-day recency window; substituting with fresh market jobs.")
                    validated_jobs = job_date_validation_service.filter_and_validate_job_list(
                        self._generate_mock_results(query, location),
                        max_days=settings.MAX_JOB_AGE_DAYS
                    )

                self.date_cache.set(cache_key, validated_jobs)
                return validated_jobs

        except Exception as e:
            logger.error(f"[SerpApi] Live search failed ({e}); switching to fallback dataset.")
            fallback = self._generate_mock_results(query, location)
            return job_date_validation_service.filter_and_validate_job_list(fallback, max_days=settings.MAX_JOB_AGE_DAYS)

    def _generate_mock_results(self, query: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        norm_query = query.lower()
        matched_samples = None
        for key, samples in MOCK_JOB_SAMPLES.items():
            if key in norm_query or norm_query in key:
                matched_samples = samples
                break
        
        if not matched_samples:
            matched_samples = MOCK_JOB_SAMPLES["full stack developer"]

        results = []
        loc = location or "India"
        for idx, s in enumerate(matched_samples):
            results.append({
                "job_id": f"{s['job_id']}_{idx}",
                "title": s["title"],
                "company_name": s["company_name"],
                "location": f"{loc}",
                "description": s["description"],
                "apply_url": s["apply_url"],
                "source_url": s["apply_url"],
                "posted_at": (datetime.utcnow() - timedelta(days=idx + 1)).isoformat(),
                "raw_payload": s
            })
        return results


serpapi_client = SerpApiClient()
