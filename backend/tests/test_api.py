import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_skills_and_roles_api():
    # Test listing roles
    roles_res = client.get("/api/v1/roles")
    assert roles_res.status_code == 200
    roles = roles_res.json()
    assert len(roles) > 0
    assert any("Full Stack" in r["name"] for r in roles)

    # Test listing skills
    skills_res = client.get("/api/v1/skills")
    assert skills_res.status_code == 200
    skills = skills_res.json()
    assert len(skills) > 0
    assert any(s["name"] == "React" for s in skills)

    # Test skill search
    search_res = client.get("/api/v1/skills/search?q=type")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert any(s["name"] == "TypeScript" for s in search_data)


def test_auth_and_profile_flow():
    email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "SecretPassword123!",
        "display_name": "Alex Developer"
    })
    assert reg_res.status_code == 201
    auth_data = reg_res.json()
    token = auth_data["access_token"]
    assert token is not None

    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # Update profile
    prof_res = client.put("/api/v1/profile", json={
        "target_role_name": "Full Stack Developer",
        "target_location": "Bengaluru",
        "skills": [
            {"name": "React", "proficiency": "advanced", "years_experience": 2.0},
            {"name": "Node.js", "proficiency": "intermediate", "years_experience": 1.5}
        ]
    }, headers=headers)
    assert prof_res.status_code == 200
    prof_data = prof_res.json()
    assert prof_data["target_role"] == "Full Stack Developer"
    assert len(prof_data["skills"]) == 2


def test_end_to_end_analysis_api():
    payload = {
        "target_role": "Full Stack Developer",
        "location": "Ahmedabad",
        "remote_preference": "flexible",
        "skills": [
            {"name": "React", "proficiency": "advanced", "years_experience": 2.0},
            {"name": "JavaScript", "proficiency": "known", "years_experience": 1.0}
        ],
        "experience_years": 1
    }
    response = client.post("/api/v1/analyses", json=payload)
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["target_role"] == "Full Stack Developer"
    assert data["jobs_analyzed"] > 0
    assert data["readiness_score"] >= 0.0
    assert len(data["market_skills"]) > 0
    assert len(data["gaps"]) > 0
    assert len(data["action_items"]) > 0
