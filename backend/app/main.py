from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.database import SessionLocal
from app.core.init_db import init_db
from app.api.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema and seed canonical dictionary on startup
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CareerRadar - Live Market Readiness & Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

from app.core.security_headers import SecurityHeadersMiddleware
from app.core.rate_limiter import RateLimitMiddleware

# Attach OWASP Security Headers & Rate Limiting Middlewares
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)

# Set CORS with localhost & loopback pattern support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else ["*"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "healthy",
        "service": "careerradar-api",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0"
    }


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def api_v1_health():
    """API v1 Health check endpoint."""
    return {
        "status": "healthy",
        "api_version": "v1",
        "serpapi_mock_mode": settings.SERPAPI_MOCK_MODE,
        "llm_provider": settings.LLM_PROVIDER
    }
