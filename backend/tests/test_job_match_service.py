import pytest
from app.models import Skill, JobSkill, Job
from app.services.job_match_service import JobMatchService


def test_alias_matching_and_canonical_resolution():
    canonical_skills = [
        Skill(id="s_aws", name="AWS", normalized_name="aws", aliases=["amazon web services", "ec2"]),
        Skill(id="s_ts", name="TypeScript", normalized_name="typescript", aliases=["ts"]),
        Skill(id="s_react", name="React", normalized_name="react", aliases=["react.js", "reactjs"]),
        Skill(id="s_node", name="Node.js", normalized_name="node.js", aliases=["node", "nodejs"]),
        Skill(id="s_pg", name="PostgreSQL", normalized_name="postgresql", aliases=["postgres", "psql"]),
    ]

    candidate_skills = [
        {"name": "Amazon Web Services", "proficiency": "advanced"},
        {"name": "React.js", "proficiency": "expert"},
        {"name": "node", "proficiency": "intermediate"},
        {"name": "Postgres", "proficiency": "beginner"},
    ]

    lookup = JobMatchService.build_candidate_skill_lookup(candidate_skills, canonical_skills)

    # AWS should be resolved to s_aws with coverage 0.90
    assert "s_aws" in lookup
    assert lookup["s_aws"]["coverage"] == 0.90
    assert lookup["s_aws"]["proficiency"] == "advanced"

    # React should be resolved to s_react with coverage 1.0
    assert "s_react" in lookup
    assert lookup["s_react"]["coverage"] == 1.0

    # Node.js should be resolved to s_node with coverage 0.70
    assert "s_node" in lookup
    assert lookup["s_node"]["coverage"] == 0.70

    # PostgreSQL should be resolved to s_pg with coverage 0.25
    assert "s_pg" in lookup
    assert lookup["s_pg"]["coverage"] == 0.25


def test_job_match_scoring_and_gap_classification():
    s_react = Skill(id="s_react", name="React", normalized_name="react", aliases=[])
    s_node = Skill(id="s_node", name="Node.js", normalized_name="node.js", aliases=[])
    s_ts = Skill(id="s_ts", name="TypeScript", normalized_name="typescript", aliases=[])
    s_aws = Skill(id="s_aws", name="AWS", normalized_name="aws", aliases=[])
    s_docker = Skill(id="s_docker", name="Docker", normalized_name="docker", aliases=[])

    # Job requirements:
    # React (required, weight 3.0)
    # Node.js (required, weight 3.0)
    # TypeScript (required, weight 3.0)
    # AWS (preferred, weight 1.5)
    # Docker (preferred, weight 1.5)
    # Total Weight = 3.0 + 3.0 + 3.0 + 1.5 + 1.5 = 12.0
    job_skills = [
        JobSkill(skill_id="s_react", importance="required"),
        JobSkill(skill_id="s_node", importance="required"),
        JobSkill(skill_id="s_ts", importance="required"),
        JobSkill(skill_id="s_aws", importance="preferred"),
        JobSkill(skill_id="s_docker", importance="preferred"),
    ]
    job_skills[0].skill = s_react
    job_skills[1].skill = s_node
    job_skills[2].skill = s_ts
    job_skills[3].skill = s_aws
    job_skills[4].skill = s_docker

    # Candidate has:
    # React = expert (coverage 1.0) -> 3.0 * 1.0 = 3.0
    # Node.js = intermediate (coverage 0.70) -> 3.0 * 0.70 = 2.1
    # AWS = beginner (coverage 0.25) -> 1.5 * 0.25 = 0.375
    # TypeScript is missing (coverage 0.0) -> 3.0 * 0.0 = 0.0
    # Docker is missing (coverage 0.0) -> 1.5 * 0.0 = 0.0
    # Covered Weight = 3.0 + 2.1 + 0.375 + 0.0 + 0.0 = 5.475
    # Overall Match Score = (5.475 / 12.0) * 100 = 45.625 -> 45.6%
    candidate_lookup = {
        "s_react": {"skill_id": "s_react", "name": "React", "proficiency": "expert", "coverage": 1.0},
        "s_node": {"skill_id": "s_node", "name": "Node.js", "proficiency": "intermediate", "coverage": 0.70},
        "s_aws": {"skill_id": "s_aws", "name": "AWS", "proficiency": "beginner", "coverage": 0.25},
    }

    result = JobMatchService.analyze_job_for_candidate(
        job_id="job_123",
        job_skills=job_skills,
        candidate_lookup=candidate_lookup
    )

    assert result["match_score"] == 45.6
    assert result["total_required_skills"] == 3
    assert result["matched_required_skills"] == 2  # React and Node.js
    assert result["missing_required_skills"] == 1  # TypeScript
    assert result["total_preferred_skills"] == 2
    assert result["weak_preferred_skills"] == 1   # AWS (beginner)
    assert result["missing_preferred_skills"] == 1 # Docker

    # Verify gap prioritization: Required missing (TypeScript) should have highest priority score
    top_gap = result["gaps"][0]
    assert top_gap["name"] == "TypeScript"
    assert top_gap["job_importance"] == "required"
    assert top_gap["gap_type"] == "missing"
