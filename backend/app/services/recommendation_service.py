from typing import List, Dict, Any, Optional
from app.models import Skill, Job, JobCandidateSkillGap
from app.core.logging import logger

SKILL_LEARNING_BRIDGES = {
    "typescript": {
        "with": ["javascript", "react", "node.js", "next.js"],
        "next_step": "Convert an existing JavaScript project to TypeScript with strict types and interfaces.",
        "practical_action": "Migrate a React or Node.js project to TypeScript. Add typed API response models, component props, and custom generics."
    },
    "next.js": {
        "with": ["react", "javascript", "typescript"],
        "next_step": "Leverage your React knowledge to build modern full-stack web applications with Next.js App Router.",
        "practical_action": "Build a Next.js application using Server Components, Server Actions, dynamic routes, and API handlers."
    },
    "docker": {
        "with": ["node.js", "python", "fastapi", "django", "express.js"],
        "next_step": "Containerize your existing backend services with multi-stage Docker builds.",
        "practical_action": "Write a production-ready Dockerfile for an API, set up docker-compose with a PostgreSQL database, and run locally."
    },
    "aws": {
        "with": ["node.js", "python", "docker", "fastapi", "express.js"],
        "next_step": "Deploy and host your backend applications on AWS core services (EC2, S3, RDS, IAM).",
        "practical_action": "Launch an EC2 instance, configure security groups and environment variables, attach an S3 bucket for assets, and deploy a live API."
    },
    "postgresql": {
        "with": ["mongodb", "sql", "node.js", "python"],
        "next_step": "Design relational database schemas with migrations, indexing, and foreign key relationships.",
        "practical_action": "Model a relational dataset using PostgreSQL and write complex JOIN queries and database indexing optimizations."
    },
    "mongodb": {
        "with": ["postgresql", "sql", "node.js", "python"],
        "next_step": "Implement flexible document-based database models and aggregation pipelines in MongoDB.",
        "practical_action": "Create a MongoDB Atlas cluster, connect via Mongoose/Motor, and implement indexing and aggregation pipelines."
    },
    "redis": {
        "with": ["node.js", "python", "fastapi", "postgresql"],
        "next_step": "Implement caching layers and background task queues with Redis.",
        "practical_action": "Add Redis caching to expensive API database queries and implement rate limiting or session storage."
    },
    "graphql": {
        "with": ["rest api", "node.js", "react", "typescript"],
        "next_step": "Design GraphQL schemas, queries, mutations, and resolvers.",
        "practical_action": "Build a GraphQL API with Apollo Server or GraphQL Yoga, implementing typed schemas and frontend queries."
    },
    "ci/cd": {
        "with": ["git", "docker", "testing"],
        "next_step": "Automate testing and deployment pipelines using GitHub Actions.",
        "practical_action": "Write a `.github/workflows/ci.yml` pipeline that lints code, runs automated tests, and builds Docker images on pull requests."
    },
    "testing": {
        "with": ["react", "node.js", "python", "javascript"],
        "next_step": "Write automated unit and integration tests for critical business logic.",
        "practical_action": "Add Jest/React Testing Library tests for frontend components or PyTest test suites for backend APIs."
    }
}


class RecommendationService:
    @classmethod
    def generate_job_recommendations(
        cls,
        job: Job,
        gaps: List[Dict[str, Any]],
        candidate_skills: List[Dict[str, Any]],
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generate actionable, job-specific recommendations that build upon the candidate's existing skills.
        """
        candidate_skill_names = [s.get("name", "").lower() for s in candidate_skills]
        recommendations = []

        # Filter to missing or weak gaps, sorted by priority
        actionable_gaps = [g for g in gaps if g["gap_type"] in ["missing", "weak"]]
        actionable_gaps.sort(key=lambda x: x["priority_score"], reverse=True)

        priority = 1
        for gap in actionable_gaps[:limit]:
            skill_name = gap["name"]
            norm_name = skill_name.lower()
            importance = gap.get("job_importance", "required")
            gap_type = gap.get("gap_type", "missing")
            freq = gap.get("market_frequency_pct", 50.0)

            bridge = SKILL_LEARNING_BRIDGES.get(norm_name)
            existing_overlap = []
            if bridge:
                existing_overlap = [s for s in bridge["with"] if s in candidate_skill_names]

            why_it_matters = (
                f"{skill_name} is listed as a {importance} requirement for this {job.title} position at {job.company_name} "
                f"(and requested in {round(freq)}% of market jobs)."
            )

            if gap_type == "missing":
                current_state = f"{skill_name} is currently missing from your candidate profile."
            else:
                current_state = f"You have {gap.get('candidate_proficiency')} proficiency in {skill_name}, which is below the desired depth for a {importance} skill."

            if bridge and existing_overlap:
                overlap_str = ", ".join(existing_overlap).title()
                recommended_next_step = f"Leverage your existing experience with {overlap_str} to master {skill_name}. {bridge['next_step']}"
                practical_action = bridge["practical_action"]
            elif bridge:
                recommended_next_step = bridge["next_step"]
                practical_action = bridge["practical_action"]
            else:
                recommended_next_step = f"Build practical proficiency in {skill_name} focused on real-world application patterns."
                practical_action = f"Create a standalone project demonstrating hands-on usage and core concepts of {skill_name}."

            evidence = f"{skill_name} is designated as '{importance}' in the {job.title} job specification."

            recommendations.append({
                "skill_id": gap["skill_id"],
                "skill_name": skill_name,
                "priority": priority,
                "why_it_matters": why_it_matters,
                "current_state": current_state,
                "recommended_next_step": recommended_next_step,
                "practical_action": practical_action,
                "evidence": evidence,
                "generated_by": "rule"
            })
            priority += 1

        return recommendations

    @classmethod
    def generate_market_recommendations(
        cls,
        market_stats: List[Dict[str, Any]],
        gaps: List[Dict[str, Any]],
        job_analyses: List[Dict[str, Any]],
        candidate_skills: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Synthesize market-level recommendations recognizing recurring gaps across multiple analyzed jobs.
        """
        # Count recurring gaps across jobs
        skill_job_deficit_count: Dict[str, int] = {}
        for ja in job_analyses:
            for g in ja.get("gaps", []):
                if g["gap_type"] in ["missing", "weak"]:
                    skill_id = g["skill_id"]
                    skill_job_deficit_count[skill_id] = skill_job_deficit_count.get(skill_id, 0) + 1

        candidate_skill_names = [s.get("name", "").lower() for s in candidate_skills]
        actionable_gaps = [g for g in gaps if g["gap_type"] in ["missing", "weak"]]

        # Score market priority = MarketFrequencyPct * (1.0 - coverage) * (1 + recurring_job_ratio)
        scored_gaps = []
        for g in actionable_gaps:
            s_id = g["skill_id"]
            freq = g["market_frequency_pct"]
            recurring_count = skill_job_deficit_count.get(s_id, 1)
            total_jobs = len(job_analyses) or 1
            recurring_ratio = recurring_count / total_jobs
            
            market_priority = freq * (1.0 + recurring_ratio)
            scored_gaps.append((market_priority, recurring_count, g))

        scored_gaps.sort(key=lambda x: x[0], reverse=True)

        recommendations = []
        priority = 1
        for score, rec_count, gap in scored_gaps[:limit]:
            skill_name = gap["name"]
            norm_name = skill_name.lower()
            freq = gap["market_frequency_pct"]
            total_jobs = len(job_analyses)

            bridge = SKILL_LEARNING_BRIDGES.get(norm_name)
            existing_overlap = [s for s in bridge["with"] if s in candidate_skill_names] if bridge else []

            why_it_matters = (
                f"Across {total_jobs} analyzed job postings, {skill_name} is requested in {round(freq)}% of positions "
                f"and represents a gap across {rec_count} specific job vacancies."
            )

            current_state = (
                f"{skill_name} is missing from your profile." if gap["gap_type"] == "missing"
                else f"You have {gap.get('candidate_proficiency')} proficiency in {skill_name}, leaving room for improvement."
            )

            if bridge and existing_overlap:
                overlap_str = ", ".join(existing_overlap).title()
                recommended_next_step = f"Build upon your {overlap_str} knowledge. {bridge['next_step']}"
                practical_action = bridge["practical_action"]
            elif bridge:
                recommended_next_step = bridge["next_step"]
                practical_action = bridge["practical_action"]
            else:
                recommended_next_step = f"Prioritize hands-on project work with {skill_name}."
                practical_action = f"Build a practical component or module utilizing {skill_name} to add to your public portfolio."

            evidence = f"{skill_name} appears in {round(freq)}% of market opportunities and in {rec_count}/{total_jobs} analyzed jobs."

            recommendations.append({
                "skill_id": gap["skill_id"],
                "skill_name": skill_name,
                "priority": priority,
                "why_it_matters": why_it_matters,
                "current_state": current_state,
                "recommended_next_step": recommended_next_step,
                "practical_action": practical_action,
                "evidence": evidence,
                "market_frequency_pct": freq,
                "recurring_jobs_count": rec_count,
                "total_jobs_analyzed": total_jobs,
                "generated_by": "rule"
            })
            priority += 1

        return recommendations


recommendation_service = RecommendationService()
