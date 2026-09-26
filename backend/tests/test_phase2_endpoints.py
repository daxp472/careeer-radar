import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_phase2_job_level_endpoints():
    # 1. Run a market analysis
    payload = {
        "target_role": "Full Stack Developer",
        "location": "Ahmedabad",
        "remote_preference": "flexible",
        "skills": [
            {"name": "React", "proficiency": "advanced", "years_experience": 2.0},
            {"name": "Node.js", "proficiency": "intermediate", "years_experience": 1.5},
            {"name": "MongoDB", "proficiency": "known", "years_experience": 1.0}
        ],
        "experience_years": 1
    }
    create_res = client.post("/api/v1/analyses", json=payload)
    assert create_res.status_code == 201
    analysis_data = create_res.json()
    analysis_id = analysis_data["id"]

    # 2. Verify Job-Level matches are present in the response
    assert len(analysis_data["job_matches"]) > 0
    first_job_match = analysis_data["job_matches"][0]
    job_id = first_job_match["job_id"]
    assert first_job_match["match_score"] >= 0.0
    assert "total_required_skills" in first_job_match

    # 3. Test GET /api/v1/analyses/{id}/jobs
    jobs_res = client.get(f"/api/v1/analyses/{analysis_id}/jobs")
    assert jobs_res.status_code == 200
    jobs_data = jobs_res.json()
    assert len(jobs_data) > 0

    # 4. Test GET /api/v1/analyses/{id}/recommendations (Market-Level Recurring Gaps)
    recs_res = client.get(f"/api/v1/analyses/{analysis_id}/recommendations")
    assert recs_res.status_code == 200
    recs_data = recs_res.json()
    assert len(recs_data) > 0
    first_rec = recs_data[0]
    assert "why_it_matters" in first_rec
    assert "practical_action" in first_rec
    assert "recurring_jobs_count" in first_rec

    # 5. Test GET /api/v1/jobs/{job_id}/analysis (Detailed Job Analysis)
    job_analysis_res = client.get(f"/api/v1/jobs/{job_id}/analysis?analysis_id={analysis_id}")
    assert job_analysis_res.status_code == 200
    job_detailed = job_analysis_res.json()
    assert job_detailed["job_id"] == job_id
    assert "match_score" in job_detailed
    assert "required_match_score" in job_detailed
    assert len(job_detailed["gaps"]) > 0
    assert len(job_detailed["recommendations"]) > 0

    # 6. Test on-demand POST /api/v1/jobs/{job_id}/analyze
    adhoc_res = client.post(f"/api/v1/jobs/{job_id}/analyze", json=[
        {"name": "React", "proficiency": "expert", "years_experience": 3.0}
    ])
    assert adhoc_res.status_code == 200
    adhoc_data = adhoc_res.json()
    assert adhoc_data["match_score"] >= 0.0
