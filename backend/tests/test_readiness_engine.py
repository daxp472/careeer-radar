import pytest
from app.services.readiness_service import ReadinessService


def test_deterministic_readiness_calculation():
    """
    Test deterministic calculation given exact numbers:
    Market:
      - React (80% frequency, importance 80)
      - AWS (60% frequency, importance 60)
      - Docker (40% frequency, importance 40)
    Total Market Importance = 80 + 60 + 40 = 180

    Candidate:
      - React = advanced (coverage 0.90) -> 80 * 0.90 = 72.0
      - AWS = missing (coverage 0.00)   -> 60 * 0.00 = 0.0
      - Docker = intermediate (coverage 0.70) -> 40 * 0.70 = 28.0
    Covered Market Importance = 72.0 + 0.0 + 28.0 = 100.0

    Readiness Score = (100.0 / 180.0) * 100 = 55.555... -> 55.6%
    """
    market_stats = [
        {"skill_id": "s1", "name": "React", "category": "Frontend", "frequency_pct": 80.0, "market_importance_score": 80.0},
        {"skill_id": "s2", "name": "AWS", "category": "Cloud", "frequency_pct": 60.0, "market_importance_score": 60.0},
        {"skill_id": "s3", "name": "Docker", "category": "DevOps", "frequency_pct": 40.0, "market_importance_score": 40.0},
    ]

    candidate_skills = {
        "s1": {"proficiency": "advanced"},
        # s2 is missing
        "s3": {"proficiency": "intermediate"},
    }

    result = ReadinessService.calculate_readiness_score(market_stats, candidate_skills)
    
    assert result["readiness_score"] == 55.6
    assert len(result["matched"]) == 2  # React (advanced >= 0.70) and Docker (intermediate >= 0.70)
    assert len(result["missing"]) == 1  # AWS
    assert result["missing"][0]["name"] == "AWS"
    assert result["missing"][0]["priority_score"] == 60.0  # 60.0 * (1.0 - 0)
