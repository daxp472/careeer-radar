# CareerRadar — Database Schema & Data Models

PostgreSQL is the single source of truth for all structured data in CareerRadar.

## Core Entities & Relational Map

1. **`users`**: System credentials, display name, and auth metadata.
2. **`candidate_profiles`**: Developer target role, target location, remote preference, years of experience.
3. **`roles`**: Target industry positions (e.g., Frontend Developer, Backend Developer, Full Stack Developer).
4. **`skills`**: Canonical skill definitions, aliases, categories, and vector embeddings.
5. **`candidate_skills`**: Candidate's claimed skills with proficiency levels (`beginner`, `known`, `intermediate`, `advanced`, `expert`).
6. **`search_runs`**: Historical snapshot of live queries dispatched to SerpApi (Google Jobs).
7. **`jobs`**: Normalized job listings with deduplication keys, freshness timestamps, and full raw JSONB payload.
8. **`search_run_jobs`**: Association table mapping jobs to search runs with relevance and search rank.
9. **`job_skills`**: Skills extracted from job descriptions, mention counts, importance level (`required`, `preferred`, `mentioned`), and extraction evidence.
10. **`market_snapshots`**: The aggregate snapshot of the market population evaluated during an analysis.
11. **`market_skill_stats`**: Statistical breakdown per skill (percentage of jobs requiring it, total mentions, importance score).
12. **`readiness_analyses`**: The computed readiness score, candidate gap summary, and snapshot link.
13. **`readiness_gaps`**: Individual skill gap classification (`matched`, `weak`, `missing`) with market priority score.
14. **`action_items`**: Actionable learning steps and project recommendations derived from verified market evidence.

---

## PostgreSQL Indexing Strategy

- `users.email` (UNIQUE, B-Tree)
- `roles.normalized_name` (UNIQUE, B-Tree)
- `skills.normalized_name` (UNIQUE, B-Tree)
- `jobs(provider, provider_job_id)` (Composite UNIQUE B-Tree)
- `jobs.normalized_title`, `jobs.company_name`, `jobs.last_seen_at`
- `job_skills(job_id, skill_id)` (Composite B-Tree)
- `candidate_skills(user_id, skill_id)` (Composite UNIQUE B-Tree)
- `market_skill_stats(snapshot_id, skill_id)` (Composite B-Tree)
- `readiness_gaps(analysis_id, skill_id)` (Composite B-Tree)
