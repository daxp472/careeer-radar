# CareerRadar — Development Guide

## 1. Prerequisites
- Python 3.11 or 3.12+
- Node.js v18+ (v20+ recommended)
- PostgreSQL 15+ (with `pgvector` extension)
- Redis 7+

## 2. Setting Up Backend
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env
```

### Running Backend Server
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Running Celery Worker
```bash
celery -A app.workers.celery_app worker --loglevel=info -P solo
```

## 3. Setting Up Frontend
```bash
cd frontend
npm install
npm run dev
```

## 4. Running Tests
```bash
cd backend
pytest -v
```
