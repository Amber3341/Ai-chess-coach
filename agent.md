# ChessMentor AI - Agent Context & Instructions

Welcome to the **ChessMentor AI** repository! This document provides structured context, guidelines, and commands for AI agents or developers working in this session.

## 1. Project Context
**ChessMentor AI** is an AI-powered full-stack chess coaching platform for intermediate players (ELO 1000–1800). Users upload a PGN game file and receive a structured, plain-English coaching report.

### Tech Stack
- **Frontend**: React 18, Vite, TypeScript, plain CSS, `react-chessboard`, `react-router-dom`. (Target Deployment: Firebase Hosting)
- **Backend API**: FastAPI (Python), SQLAlchemy, Alembic, JWT Auth.
- **Async & Cloud Architecture**: BackgroundTasks (local fallback) / GCP Pub/Sub + Cloud Run (production).
- **Storage & Database**: SQLite (local dev) / Neon PostgreSQL (production), GCP Cloud Storage (PGNs).
- **AI/Chess Engines**:
  - Stockfish 16 (via `python-chess`) for position evaluation.
  - Gemini Embeddings (`gemini-embedding-001`) + Qdrant Cloud for RAG over 61 chess theory passages.
  - Google Gemini 2.5 Flash for generating the final coaching report.

## 2. Current State of the Project
**Milestone**: Cloud-connected MVP.
The core product flow is functional end-to-end:
1. User authenticates via JWT or Google OAuth.
2. Uploads a PGN -> saved to GCS (or local).
3. Analysis job is dispatched to GCP Pub/Sub (or local BackgroundTask).
4. Worker pipeline runs: Stockfish eval -> RAG Retrieval -> Gemini 2.5 Flash report generation.
5. Frontend polls for completion and displays interactive chessboards and coaching advice.

*Refer to the `README.md` and `ai_agent.md` for a complete breakdown of implemented and pending features.*

## 3. Rules to Follow While Making Changes
1. **Frontend vs Backend Split**: Always ensure you are working in the correct directory. Frontend code lives in `/frontend`, backend code lives in `/api`, worker pipelines in `/worker`, and scripts in `/scripts`.
2. **Environment Variables**: Never hardcode secrets. Always read from `config.py` in the backend, and update `.env.example` if you introduce a new required variable.
3. **Async Practices**: FastAPI relies heavily on async code. Do not run blocking I/O (like long PGN parsing or Stockfish) in the main thread during request handling. Always use background tasks or Pub/Sub workers.
4. **Error Handling**: Use appropriate HTTP exceptions in the API. In the worker pipeline, ensure errors gracefully fallback (e.g., if Gemini is down, the system should fall back to deterministic Stockfish-only reporting).
5. **Testing**: Write or update tests in `/tests` when introducing new logic. Ensure `pytest` passes locally.

## 4. Common Mistakes to Look Out For
- **Gemini API Rate Limiting (429)**: The free tier has limits (15-20 req/day on some accounts). If you encounter `429 RESOURCE_EXHAUSTED`, ensure the fallback Stockfish pipeline is triggered properly instead of crashing the worker.
- **Database Session Leaks in BackgroundTasks**: BackgroundTasks MUST create their own SQLAlchemy session independent of the request lifecycle. Do not pass the request's `db: Session` into a background worker.
- **Missing Local Dependencies**: Ensure Stockfish is installed on the local system and `STOCKFISH_PATH` is correctly set in `.env` if not in the system PATH.
- **CORS Issues**: When testing the frontend against a local or deployed backend, ensure `CORS_ORIGINS` in the backend's `.env` matches the frontend URL.
- **Relative Imports**: The Python backend uses absolute imports (e.g., `from api.models import User`). Do not use relative imports like `from ..models import User` across top-level modules.

## 5. AI Agent Workflow Protocol (CRITICAL)
Whenever a user requests a new feature, UI overhaul, or complex bug fix, you MUST default to the **Multi-Agent Branched Workflow** without asking the user to manually request it. 

**The Workflow:**
1. **Plan**: Formally draft an `implementation_plan.md` and wait for user approval.
2. **Track**: Create a `task.md` to track progress.
3. **Branch & Code**: Use `invoke_subagent` to spawn a "Coder" subagent in a `branch` workspace. Instruct the Coder to implement the feature.
4. **Review**: Once the Coder finishes, the main agent MUST step in as the **Reviewer**. Run `git status` and `git diff` on the Coder's branched workspace to heavily scrutinize the code. If errors are found, send a message to the Coder to fix them.
5. **Merge**: Once the code is flawless, use `Copy-Item` or `git` to merge the Coder's files into the main workspace.
6. **Walkthrough**: Generate a `walkthrough.md` explaining the final results.

## 6. Useful Commands

### 🐍 Backend & Worker Setup (Root Directory)
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend locally
uvicorn api.main:app --reload

# Run Pytest suite
pytest
```

### ⚛️ Frontend Setup (`/frontend` Directory)
```powershell
cd frontend

# Install dependencies
npm install

# Run Vite dev server
npm run dev
```

### 🧠 Database & Scripts
```powershell
# Ingest 61 chess theory passages into Qdrant using Gemini Embeddings
python scripts/ingest_theory.py

# Run Alembic migrations (if DB models changed)
alembic upgrade head
```

---
*Note for AI Agents: Always read this file before beginning work in a new session to re-orient yourself to the project's architecture, tools, and pitfalls.*
