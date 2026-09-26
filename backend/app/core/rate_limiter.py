import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger


class SlidingWindowRateLimiter:
    """
    Thread-safe, sliding-window in-memory rate limiter with per-route limits and IP tracking.
    """
    def __init__(self):
        # ip -> list of timestamps
        self._records: Dict[str, List[float]] = defaultdict(list)
        
        # Route prefix / path patterns to limit (requests, window_seconds)
        self.rules: List[Tuple[str, int, int]] = [
            ("/api/v1/auth/login", 20, 60),          # 20 logins / min
            ("/api/v1/auth/register", 15, 60),       # 15 registrations / min
            ("/api/v1/analyses", 25, 60),            # 25 market analyses / min
            ("/api/v1/automation/scan-now", 15, 60), # 15 manual scans / min
            ("/api/v1/jobs/admin/refresh", 5, 60),   # 5 manual refreshes / min
            ("/api/v1", 200, 60),                    # 200 general requests / min
        ]

    def get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        return request.client.host if request.client else "127.0.0.1"

    def match_rule(self, path: str) -> Tuple[int, int]:
        for prefix, max_reqs, window_secs in self.rules:
            if path.startswith(prefix):
                return max_reqs, window_secs
        return 200, 60

    def check_rate_limit(self, client_ip: str, path: str) -> Tuple[bool, int, int, int]:
        """
        Returns: (is_allowed, limit, remaining, retry_after)
        """
        max_reqs, window_secs = self.match_rule(path)
        now = time.time()
        window_start = now - window_secs
        key = f"{client_ip}:{path}"

        # Clean timestamps older than window_start
        timestamps = self._records[key]
        valid_timestamps = [t for t in timestamps if t > window_start]
        self._records[key] = valid_timestamps

        if len(valid_timestamps) >= max_reqs:
            oldest_in_window = valid_timestamps[0]
            retry_after = max(1, int(window_secs - (now - oldest_in_window)))
            return False, max_reqs, 0, retry_after

        # Record this request
        valid_timestamps.append(now)
        remaining = max(0, max_reqs - len(valid_timestamps))
        return True, max_reqs, remaining, 0

    def reset(self):
        self._records.clear()


rate_limiter = SlidingWindowRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Skip docs, openapi, and static health checks
        if path in ("/docs", "/redoc", "/health", "/api/v1/health") or path.startswith("/static") or request.method == "OPTIONS":
            return await call_next(request)

        client_ip = rate_limiter.get_client_ip(request)
        is_allowed, limit, remaining, retry_after = rate_limiter.check_rate_limit(client_ip, path)

        if not is_allowed:
            logger.warning(f"[RateLimit] 429 Too Many Requests: IP={client_ip} Path={path} RetryAfter={retry_after}s")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded ({limit} requests per minute). Please retry in {retry_after} seconds.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0"
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
