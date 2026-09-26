from fastapi import APIRouter
from app.api.routes import auth, skills, profiles, analyses, jobs, watchlist, automation, notifications

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(skills.router)
api_router.include_router(profiles.router)
api_router.include_router(analyses.router)
api_router.include_router(jobs.router)
api_router.include_router(watchlist.router)
api_router.include_router(automation.router)
api_router.include_router(notifications.router)

