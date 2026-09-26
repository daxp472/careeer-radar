from app.models.user import User
from app.models.role import Role
from app.models.skill import Skill
from app.models.candidate_profile import CandidateProfile
from app.models.candidate_skill import CandidateSkill
from app.models.job import Job
from app.models.search_run import SearchRun
from app.models.search_run_job import SearchRunJob
from app.models.job_skill import JobSkill
from app.models.market_snapshot import MarketSnapshot
from app.models.market_skill_stat import MarketSkillStat
from app.models.readiness_analysis import ReadinessAnalysis
from app.models.readiness_gap import ReadinessGap
from app.models.action_item import ActionItem
from app.models.job_candidate_analysis import JobCandidateAnalysis
from app.models.job_candidate_skill_gap import JobCandidateSkillGap
from app.models.job_candidate_recommendation import JobCandidateRecommendation
from app.models.watchlist import Watchlist
from app.models.skill_progress_history import SkillProgressHistory
from app.models.candidate_job_alert_settings import CandidateJobAlertSettings
from app.models.candidate_job_scan import CandidateJobScan
from app.models.notification import Notification
from app.models.job_ingestion_report import JobIngestionReport

__all__ = [
    "User",
    "Role",
    "Skill",
    "CandidateProfile",
    "CandidateSkill",
    "Job",
    "SearchRun",
    "SearchRunJob",
    "JobSkill",
    "MarketSnapshot",
    "MarketSkillStat",
    "ReadinessAnalysis",
    "ReadinessGap",
    "ActionItem",
    "JobCandidateAnalysis",
    "JobCandidateSkillGap",
    "JobCandidateRecommendation",
    "Watchlist",
    "SkillProgressHistory",
    "CandidateJobAlertSettings",
    "CandidateJobScan",
    "Notification",
    "JobIngestionReport",
]
