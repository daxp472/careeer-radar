# CareerRadar — System Architecture

## 1. Overview & Core Philosophy

CareerRadar is a **live market-readiness intelligence platform** for students, graduates, self-taught developers, and early-career developers. 

The core mission:
> **"Turn the live technology job market into a practical signal that helps a developer understand where they currently stand and what skills they may need to improve."**

Unlike traditional job boards that solely match and list jobs, CareerRadar analyzes live market demand, aggregates real-time job skill requirements, deterministically evaluates candidate skill coverage, and uses AI as an explanatory layer.

```
LIVE MARKET DATA (SerpApi / Google Jobs)
                ↓
    JOB NORMALIZATION & DEDUPLICATION
                ↓
SKILL EXTRACTION (Canonical Skills & Aliases)
                ↓
MARKET AGGREGATION (Frequency & Importance)
                ↓
    CANDIDATE SKILLS COMPARISON
                ↓
DETERMINISTIC READINESS ENGINE (Weighted Coverage Formula)
                ↓
       AI EXPLANATION LAYER (Structured Evidence Prompt)
                ↓
    ACTIONABLE MARKET READINESS INTELLIGENCE
```

---

## 2. High-Level Architecture (Modular Monolith)

```
                    ┌─────────────────────────┐
                    │      Next.js App        │
                    │    (React / TS / TW)    │
                    └────────────┬────────────┘
                                 │ REST / JSON
                                 ▼
                    ┌─────────────────────────┐
                    │     FastAPI Backend     │
                    │   (Python 3.11/3.12+)   │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
  PostgreSQL                SerpApi (Jobs)             Redis
 (+ pgvector)                    │                    (Queue)
  Source of Truth                │                       │
                                 │                       ▼
                                 │                 Celery Workers
                                 │                       │
                                 ▼                       ▼
                         Live Market Data        Analysis Pipeline
                                                         │
                                                         ▼
                                                    LLM Provider
                                               (Explanatory Only)
```

---

## 3. Technology Stack

- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, Lucide Icons, Lightweight Visualizations.
- **Backend**: FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, httpx.
- **Database**: PostgreSQL with `pgvector` for semantic skill assistance.
- **Queue / Async**: Redis 7+, Celery 5.x.
- **Live Search**: SerpApi (Google Jobs engine) with Mock Provider for development/testing.
- **AI Integration**: Structured LLM layer for generating clear explanations and learning next steps without modifying deterministic math.
