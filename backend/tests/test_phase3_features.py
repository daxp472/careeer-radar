import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.services.candidate_scan_service import candidate_scan_service

client = TestClient(app)


def test_timezone_aware_next_scan_calculation():
    """
    Test requirement 53: Next scan calculation must be timezone-aware.
    """
    # Test Monday 10 AM Asia/Kolkata
    next_mon = candidate_scan_service.calculate_next_scan_at(
        day_of_week="Monday",
        time_of_day="10:00",
        timezone_str="Asia/Kolkata"
    )
    assert next_mon is not None
    assert isinstance(next_mon, datetime)
    assert next_mon > datetime.now(timezone.utc).replace(tzinfo=None)

    # Test Friday 18:00 America/New_York
    next_fri = candidate_scan_service.calculate_next_scan_at(
        day_of_week="Friday",
        time_of_day="18:00",
        timezone_str="America/New_York"
    )
    assert next_fri is not None
    assert next_fri > datetime.now(timezone.utc).replace(tzinfo=None)


def test_phase3_database_search_and_admin_status():
    """
    Test database search without SerpApi invocation and admin monitoring.
    """
    # 1. Admin status check
    status_res = client.get("/api/v1/jobs/admin/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert "total_active_jobs" in status_data
    assert "total_jobs" in status_data
    assert "recent_reports" in status_data

    # 2. Database search
    search_res = client.get("/api/v1/jobs/search?limit=10")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert "total" in search_data
    assert "jobs" in search_data
    assert "applied_filters" in search_data
    assert search_data["page"] == 1


def test_phase3_full_candidate_workflow():
    """
    End-to-end test for user registration, profile skill evolution,
    watchlist saving/recalculation, automation settings, manual scan, and in-app notifications.
    """
    # 1. Register & Login test user
    email = f"test_candidate_{datetime.now().timestamp()}@careerradar.io"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "display_name": "Test Candidate"
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update Candidate Profile with initial skills
    profile_payload = {
        "target_role": "Full Stack Developer",
        "location": "Ahmedabad, India",
        "remote_preference": "flexible",
        "experience_years": 2,
        "skills": [
            {"name": "React", "proficiency": "beginner", "years_experience": 1.0},
            {"name": "Node.js", "proficiency": "beginner", "years_experience": 1.0}
        ]
    }
    prof_res = client.put("/api/v1/profile", json=profile_payload, headers=headers)
    assert prof_res.status_code == 200

    # 3. Check Skill Progress History
    prog_res = client.get("/api/v1/profile/progress", headers=headers)
    assert prog_res.status_code == 200
    prog_data = prog_res.json()
    assert len(prog_data) >= 2
    # Verify beginner was logged
    skill_names = [p["skill_name"] for p in prog_data]
    assert "React" in skill_names

    # 4. Update Profile Skill: React beginner -> advanced
    profile_payload["skills"] = [
        {"name": "React", "proficiency": "advanced", "years_experience": 2.5},
        {"name": "Node.js", "proficiency": "intermediate", "years_experience": 2.0},
        {"name": "TypeScript", "proficiency": "intermediate", "years_experience": 1.5}
    ]
    prof_res2 = client.put("/api/v1/profile", json=profile_payload, headers=headers)
    assert prof_res2.status_code == 200

    # Verify skill progress timeline has new entries
    prog_res2 = client.get("/api/v1/profile/progress", headers=headers)
    assert prog_res2.status_code == 200
    prog_data2 = prog_res2.json()
    react_entries = [p for p in prog_data2 if p["skill_name"] == "React"]
    assert len(react_entries) >= 2
    assert react_entries[0]["to_proficiency"] == "advanced"
    assert react_entries[0]["from_proficiency"] == "beginner"

    # 5. Search Database Jobs with candidate match scores
    search_res = client.get("/api/v1/jobs/search?sort=match_score&limit=5", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    if search_data["jobs"]:
        first_job = search_data["jobs"][0]
        assert "match_score" in first_job
        job_id = first_job["id"]

        # 6. Save job to Watchlist
        watch_res = client.post(f"/api/v1/watchlist/{job_id}", headers=headers)
        assert watch_res.status_code in [200, 201]

        # 7. Get Watchlist and check dynamic match calculation
        watchlist_get = client.get("/api/v1/watchlist", headers=headers)
        assert watchlist_get.status_code == 200
        saved_items = watchlist_get.json()
        assert len(saved_items) >= 1
        assert saved_items[0]["job_id"] == job_id
        assert saved_items[0]["match_score"] is not None

        # 8. Remove from Watchlist
        del_watch = client.delete(f"/api/v1/watchlist/{job_id}", headers=headers)
        assert del_watch.status_code == 200

    # 9. Configure Candidate Automation Settings (Weekly Job Radar)
    settings_payload = {
        "enabled": True,
        "frequency": "weekly",
        "day_of_week": "Monday",
        "time_of_day": "10:00",
        "timezone": "Asia/Kolkata",
        "minimum_match_score": 70.0,
        "email_enabled": True,
        "in_app_enabled": True
    }
    set_res = client.put("/api/v1/automation/settings", json=settings_payload, headers=headers)
    assert set_res.status_code == 200
    set_data = set_res.json()
    assert set_data["enabled"] is True
    assert set_data["day_of_week"].lower() == "monday"
    assert set_data["minimum_match_score"] == 70.0
    assert set_data["next_scan_at"] is not None

    # 10. Execute Manual Scan Now
    scan_res = client.post("/api/v1/automation/scan-now", headers=headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()
    assert scan_data["status"] == "completed"
    assert "jobs_checked" in scan_data

    # 11. Check Scan History
    history_res = client.get("/api/v1/automation/scans", headers=headers)
    assert history_res.status_code == 200
    scans_list = history_res.json()
    assert len(scans_list) >= 1

    # 12. Check In-App Notifications
    notif_res = client.get("/api/v1/notifications", headers=headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()
    assert "notifications" in notifs
    assert "unread_count" in notifs

    # 13. Mark notifications as read
    if notifs["notifications"]:
        notif_id = notifs["notifications"][0]["id"]
        patch_res = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=headers)
        assert patch_res.status_code == 200

    # Mark all read
    read_all_res = client.patch("/api/v1/notifications/read-all", headers=headers)
    assert read_all_res.status_code == 200
