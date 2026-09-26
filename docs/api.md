# CareerRadar — REST API Specification

All endpoints are versioned under `/api/v1`.

## Core Endpoints

### Health
- `GET /health` — Global health check
- `GET /api/v1/health` — API v1 status and provider modes

### Authentication
- `POST /api/v1/auth/register` — Register a new developer account
- `POST /api/v1/auth/login` — Authenticate and receive JWT
- `POST /api/v1/auth/logout` — Revoke / clear session
- `GET /api/v1/auth/me` — Retrieve active user session

### Candidate Profiles
- `GET /api/v1/profile` — Fetch current candidate profile and skills
- `PUT /api/v1/profile` — Update target role, location, remote preference
- `POST /api/v1/profile/skills` — Add or update a candidate skill & proficiency
- `DELETE /api/v1/profile/skills/{skill_id}` — Remove a candidate skill

### Roles & Skills Dictionary
- `GET /api/v1/roles` — List supported career roles
- `GET /api/v1/skills` — Browse canonical skills
- `GET /api/v1/skills/search?q={query}` — Search skills with alias resolution

### Searches & Market Analysis
- `POST /api/v1/searches` — Initiate live job discovery run
- `GET /api/v1/searches/{id}/status` — Poll search and ingestion lifecycle
- `POST /api/v1/analyses` — Trigger deterministic market readiness evaluation
- `GET /api/v1/analyses/{id}` — Retrieve full readiness report
- `GET /api/v1/analyses/{id}/market` — Retrieve market snapshot breakdown
- `GET /api/v1/analyses/{id}/gaps` — Retrieve classified skill gaps (matched, weak, missing)
- `GET /api/v1/analyses/{id}/actions` — Retrieve evidence-backed action plan recommendations
