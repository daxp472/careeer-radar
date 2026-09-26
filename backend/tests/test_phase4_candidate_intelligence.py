import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_phase4_what_changed_and_feedback_flow():
    # 1. Register candidate
    email = f"intel_candidate_{datetime.now().timestamp()}@careerradar.io"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "display_name": "Intelligence Candidate"
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Run Baseline Market Analysis (Analysis 1: Beginner Skills)
    payload_1 = {
        "target_role": "Full Stack Developer",
        "location": "Ahmedabad",
        "remote_preference": "flexible",
        "skills": [
            {"name": "React", "proficiency": "beginner", "years_experience": 0.5},
            {"name": "Node.js", "proficiency": "beginner", "years_experience": 0.5}
        ],
        "experience_years": 0
    }
    res_1 = client.post("/api/v1/analyses", json=payload_1, headers=headers)
    assert res_1.status_code == 201
    analysis_1 = res_1.json()
    id_1 = analysis_1["id"]

    # 3. Test Baseline Diff (should have has_previous_analysis = False)
    diff_res_1 = client.get(f"/api/v1/analyses/{id_1}/diff", headers=headers)
    assert diff_res_1.status_code == 200
    diff_1 = diff_res_1.json()
    assert diff_1["has_previous_analysis"] is False
    assert diff_1["readiness_score_change"] == 0.0
    assert "baseline" in diff_1["summary"].lower()

    # 4. Run Second Market Analysis (Analysis 2: Upgraded Skills + TypeScript added)
    payload_2 = {
        "target_role": "Full Stack Developer",
        "location": "Ahmedabad",
        "remote_preference": "flexible",
        "skills": [
            {"name": "React", "proficiency": "advanced", "years_experience": 2.0},
            {"name": "Node.js", "proficiency": "intermediate", "years_experience": 1.5},
            {"name": "TypeScript", "proficiency": "intermediate", "years_experience": 1.0},
            {"name": "PostgreSQL", "proficiency": "known", "years_experience": 1.0}
        ],
        "experience_years": 1
    }
    res_2 = client.post("/api/v1/analyses", json=payload_2, headers=headers)
    assert res_2.status_code == 201
    analysis_2 = res_2.json()
    id_2 = analysis_2["id"]

    # 5. Test What Changed Diff between Analysis 2 and Analysis 1
    diff_res_2 = client.get(f"/api/v1/analyses/{id_2}/diff", headers=headers)
    assert diff_res_2.status_code == 200
    diff_2 = diff_res_2.json()
    assert diff_2["has_previous_analysis"] is True
    assert diff_2["previous_analysis_id"] == id_1
    assert diff_2["current_readiness_score"] >= diff_2["previous_readiness_score"]
    assert diff_2["readiness_score_change"] >= 0.0

    # Verify skill improvements detected
    improved_names = [s["skill_name"] for s in diff_2["improved_proficiencies"]]
    assert "React" in improved_names or "Node.js" in improved_names

    # 6. Test Structured Candidate Feedback Report
    feedback_res = client.get(f"/api/v1/analyses/{id_2}/feedback", headers=headers)
    assert feedback_res.status_code == 200
    report = feedback_res.json()

    assert report["analysis_id"] == id_2
    assert "alignment_tier" in report
    assert "current_position" in report
    assert "strongest_areas" in report
    assert "biggest_gaps" in report
    assert "what_changed" in report
    assert "market_signals" in report
    assert "personalized_action_plan" in report

    # Verify section details
    assert len(report["current_position"]["items"]) > 0
    assert len(report["strongest_areas"]["items"]) > 0
    assert len(report["personalized_action_plan"]) > 0
