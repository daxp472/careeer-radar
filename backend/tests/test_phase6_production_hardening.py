import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.services.readiness_service import readiness_service
from app.services.job_match_service import job_match_service
from app.models import Skill

client = TestClient(app)


def test_matching_edge_cases_and_zero_skills():
    """
    Test Section 6.2 & 6.3: Deterministic matching across edge cases.
    """
    # 1. Zero candidate skills -> 0% readiness
    market_stats = [
        {"skill_id": "sk1", "name": "React", "category": "Frontend", "frequency_pct": 80.0, "market_importance_score": 80.0},
        {"skill_id": "sk2", "name": "Node.js", "category": "Backend", "frequency_pct": 70.0, "market_importance_score": 70.0}
    ]
    empty_lookup = {}
    res_empty = readiness_service.calculate_readiness_score(market_stats, empty_lookup)
    assert res_empty["readiness_score"] == 0.0
    assert len(res_empty["missing"]) == 2
    assert len(res_empty["matched"]) == 0

    # 2. Expert proficiency on all skills -> 100% readiness
    expert_lookup = {
        "sk1": {"proficiency": "expert"},
        "sk2": {"proficiency": "expert"}
    }
    res_expert = readiness_service.calculate_readiness_score(market_stats, expert_lookup)
    assert res_expert["readiness_score"] == 100.0
    assert len(res_expert["matched"]) == 2
    assert len(res_expert["missing"]) == 0

    # 3. Beginner proficiency (0.25 weight) -> 25% readiness
    beginner_lookup = {
        "sk1": {"proficiency": "beginner"},
        "sk2": {"proficiency": "beginner"}
    }
    res_beg = readiness_service.calculate_readiness_score(market_stats, beginner_lookup)
    assert res_beg["readiness_score"] == 25.0
    assert len(res_beg["weak"]) == 2

    # 4. Required vs Preferred skill differentiation
    # In JobMatchService: required skills have 80% weight, preferred have 20%
    job_skills_dummy = [
        type("JobSkillMock", (), {"skill_id": "sk1", "importance": "required", "skill": type("SkillMock", (), {"id": "sk1", "name": "React", "category": "Frontend"})()})(),
        type("JobSkillMock", (), {"skill_id": "sk2", "importance": "preferred", "skill": type("SkillMock", (), {"id": "sk2", "name": "Docker", "category": "DevOps"})()})()
    ]
    # Candidate matches only the preferred skill (Docker), missing required (React)
    docker_only_lookup = {"sk2": {"name": "Docker", "proficiency": "expert"}}
    analysis_pref_only = job_match_service.analyze_job_for_candidate("job1", job_skills_dummy, docker_only_lookup)
    assert analysis_pref_only["required_match_score"] == 0.0
    assert analysis_pref_only["preferred_match_score"] == 100.0
    assert analysis_pref_only["match_score"] == 33.3  # 1.5 / 4.5 = 33.3%

    # Candidate matches only the required skill (React), missing preferred (Docker)
    react_only_lookup = {"sk1": {"name": "React", "proficiency": "expert"}}
    analysis_req_only = job_match_service.analyze_job_for_candidate("job1", job_skills_dummy, react_only_lookup)
    assert analysis_req_only["required_match_score"] == 100.0
    assert analysis_req_only["preferred_match_score"] == 0.0
    assert analysis_req_only["match_score"] == 66.7  # 3.0 / 4.5 = 66.7%


def test_candidate_isolation_and_security():
    """
    Test Section 6.14: Candidate A cannot access or tamper with Candidate B's data.
    """
    # 1. Register Candidate A
    email_a = f"candidate_a_{datetime.now().timestamp()}@careerradar.io"
    res_a = client.post("/api/v1/auth/register", json={
        "email": email_a,
        "password": "Password123!",
        "display_name": "Candidate A"
    })
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register Candidate B
    email_b = f"candidate_b_{datetime.now().timestamp()}@careerradar.io"
    res_b = client.post("/api/v1/auth/register", json={
        "email": email_b,
        "password": "Password123!",
        "display_name": "Candidate B"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Candidate A updates automation settings
    client.put("/api/v1/automation/settings", json={
        "enabled": True,
        "day_of_week": "Friday",
        "minimum_match_score": 85.0
    }, headers=headers_a)

    # Candidate B checks settings - must be isolated default, NOT Candidate A's settings
    settings_b = client.get("/api/v1/automation/settings", headers=headers_b).json()
    assert settings_b["user_id"] != res_a.json()["user"]["id"]
    assert settings_b["minimum_match_score"] == 80.0  # default for B, not A's 85.0

    # Candidate A notifications must not leak to Candidate B
    client.post("/api/v1/automation/scan-now", headers=headers_a)
    notifs_b = client.get("/api/v1/notifications", headers=headers_b).json()
    assert len(notifs_b["notifications"]) == 0  # Candidate B has 0 notifications


def test_production_health_endpoints():
    """
    Test Section 6.18: Production health checks.
    """
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert res1.json()["status"] == "healthy"

    res2 = client.get("/api/v1/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "healthy"
