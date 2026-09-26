# CareerRadar 🎯

> **Live Market-Readiness Intelligence Platform for Developers**

CareerRadar bridges the gap between software developers and real-world tech job requirements. Instead of merely listing job openings, CareerRadar continuously ingests live job listings via **SerpApi (Google Jobs)**, standardizes skills, computes deterministic market readiness coverage, and uses AI to deliver evidence-backed career gap explanations and actionable project roadmaps.

---

## 🌟 Key Features

1. **Live Market Ingestion**: Discovers live opportunities matching specific target roles and locations.
2. **Deterministic Readiness Engine**: Transparent, mathematically grounded market-readiness scoring (never arbitrary AI hallucinations).
3. **Skill Gap Intelligence**: Automatically flags skills as `Matched`, `Weak`, or `Missing` against real employer demand.
4. **Evidence-Backed Action Plans**: Generates structured, prioritized next steps grounded in live market statistics.
5. **Modern Tech Stack**: Next.js (App Router, Tailwind CSS, TypeScript) + FastAPI (SQLAlchemy 2, Alembic, PostgreSQL, pgvector, Redis, Celery).

---

## 🏗️ Architecture & Data Pipeline

```
  LIVE JOBS (SerpApi)
          ↓
  NORMALIZATION & DEDUPLICATION
          ↓
  CANONICAL SKILL EXTRACTION
          ↓
  MARKET FREQUENCY AGGREGATION
          ↓
  CANDIDATE SKILL COMPARISON
          ↓
  DETERMINISTIC READINESS SCORING
          ↓
  LLM EXPLANATION & ACTION ITEMS
          ↓
  INTERACTIVE RESULT DASHBOARD
```

---

## 🚀 Quickstart

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### 1. Clone & Setup Environment
```bash
cp .env.example .env
```

### 2. Run Backend
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to interact with the application.
API documentation is available at `http://localhost:8000/docs`.

---

## 📚 Documentation
Detailed technical documentation is available in the [`docs/`](file:///d:/client/Serp%20API/docs) directory:
- [Architecture Documentation](file:///d:/client/Serp%20API/docs/architecture.md)
- [Database Schema & Models](file:///d:/client/Serp%20API/docs/database.md)
- [Analysis Engine & Scoring Formulas](file:///d:/client/Serp%20API/docs/analysis-engine.md)
- [REST API Specifications](file:///d:/client/Serp%20API/docs/api.md)
- [AI Orchestration Guidelines](file:///d:/client/Serp%20API/docs/ai.md)
- [Local Development Guide](file:///d:/client/Serp%20API/docs/development.md)
