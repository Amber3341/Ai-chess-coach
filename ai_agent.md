# AI Agent Context Document: ChessMentor AI

This document serves as the primary context reference for AI agents working on the ChessMentor AI project. It summarises the project's goals, architecture, current implementation status, and remaining work based on the PRD, HLD, LLD, and UI Wireframes.

## 1. Project Overview
**Name**: ChessMentor AI  
**Purpose**: An AI-powered full-stack chess coaching platform for intermediate players (ELO 1000–1800). Users upload a PGN game file and receive a structured, plain-English coaching report within 60 seconds.  
**Goal**: A production-grade portfolio project showcasing GenAI, backend engineering, and cloud deployment.

### Tech Stack
- **Frontend**: React 18, Vite, TypeScript, CSS, react-chessboard, react-router-dom. (Target Deployment: Firebase Hosting)
- **Backend API**: FastAPI (Python), JWT Auth. (Target Deployment: GCP Cloud Run)
- **Async Workers**: FastAPI BackgroundTasks (local). Target: GCP Pub/Sub + Cloud Run Worker.
- **Storage & Database**: SQLite (local dev), target Neon DB / PostgreSQL. GCP Cloud Storage (PGNs). Qdrant Cloud (Vector DB).
- **AI/Chess Engines**:
  - Stockfish 16 (position evaluation via `python-chess`)
  - Google Gemini Embeddings API (`gemini-embedding-001`, 3072-dim, via `google-genai`)
  - Qdrant Cloud (vector DB storing 61 chess theory passages)
  - Google Gemini 2.5 Flash (LLM for generating coaching reports)

## 2. Architecture & Design
- **Async Job Flow (current local implementation)**:
  1. Frontend POSTs PGN file to API → `POST /api/v1/games`.
  2. API validates PGN, saves file locally, writes a `pending` game record to DB.
  3. Frontend calls `POST /api/v1/games/{id}/analyze`.
  4. API marks game as `processing`, immediately returns `202 Accepted`.
  5. FastAPI `BackgroundTasks` runs Stockfish + RAG + Gemini pipeline in a background thread.
  6. Stockfish evaluates all moves, identifies critical moments (blunders, mistakes, inaccuracies).
  7. RAG: critical moment is embedded via Gemini Embeddings API, queried against Qdrant `chess-theory` collection (top-3 passages returned).
  8. Gemini 2.5 Flash receives Stockfish data + RAG theory passages → generates structured coaching report (summary, phase reviews, coach notes, action plan).
  9. Report saved to DB, game status set to `complete`.
  10. Frontend polls `GET /api/v1/games/{id}` every 2s until `status != "processing"`, then fetches report.
- **Database Schema**: `users`, `games`, `move_evaluations` (SQLAlchemy ORM, Alembic migrations).
- **UI Screens**: Login/Register, Dashboard (Game List + Upload), Analysis Loading (polling), Coaching Report (Summary, Critical Moments, Phase Reviews, Action Plan, Full Replay).

## 3. Current Implementation Status
The project is currently at the **Local AI MVP stage — Core AI pipeline fully functional**.

### 3.1 Implemented ✅

#### Authentication & Users
- JWT-based registration and login (`/api/v1/auth/register`, `/api/v1/auth/login`).
- All game routes secured — data scoped to authenticated user.
- `AuthContext` + `ProtectedRoute` in the React frontend.
- Login and Register pages with form validation.
- Alembic database migrations (`dev_v2.db`).

#### Backend API (FastAPI)
- Health check, CORS, and `/api/v1` prefix.
- SQLite + SQLAlchemy + Alembic migrations.
- PGN upload with validation (UTF-8, extension check, 150-move MVP limit).
- Game state machine: `pending` → `processing` → `complete` / `failed`.
- `POST /api/v1/games/{id}/analyze` returns **202 Accepted immediately** — analysis is async.
- Report, moves, and game list endpoints (all user-scoped).

#### Analysis Pipeline (Worker)
- **Stockfish** integration (`python-chess` UCI) with material-balance fallback.
- **Gemini 2.5 Flash** coaching report generation via `google-genai` SDK.
- **RAG Pipeline**: 61 chess theory passages embedded (Gemini `gemini-embedding-001`, 3072-dim) and stored in Qdrant Cloud. Retrieved at analysis time for theory-grounded advice.
- Graceful fallback: if Gemini/Qdrant unavailable, falls back to deterministic rule-based report.
- `source_detail` field in report metadata shows `"Coaching provided by Gemini 2.5 Flash + RAG"` when both systems are active.

#### Async Architecture
- `FastAPI BackgroundTasks` runs the full pipeline (Stockfish + RAG + Gemini) in a background thread.
- Background task creates its own DB session (independent of request lifecycle).
- `database_url` passed explicitly to background task so tests can inject test DB.

#### Frontend (React/Vite/TypeScript)
- `react-router-dom` routing with `ProtectedRoute`.
- `AuthContext` for global user state; auto-redirect on `401 Unauthorized`.
- `AuthPages.tsx` with Login and Register forms.
- `api.ts` injects `Authorization: Bearer <token>` in all requests.
- `pollUntilComplete()` helper polls every 2s until analysis finishes.
- `handleAnalyze` shows live progress message: *"Running Stockfish evaluation + AI coaching (this may take ~30s)..."*
- Full coaching report view: summary, critical moments with FEN boards, phase reviews, action plan, move replay.
- Game history sidebar with search and status filters.

#### Scripts
- `scripts/chess_theory.py` — 61 curated theory passages (openings, tactics, middlegame, endgame, king safety, rooks).
- `scripts/ingest_theory.py` — one-time ingestion script; batch-embeds passages and uploads to Qdrant.

#### Testing
- 7 automated tests (pytest + HTTPX TestClient).
- All routes tested with mocked auth and test DB.
- Background task tested with monkeypatched `database_url`.

## 4. Pending Implementations (To-Do)

### 4.1 Product Features (Remaining)
- **Pagination**: Paginated responses on game history (currently returns all games).
- **Multiple PGNs in one file**: Parser only handles the first game.
- **Exportable reports**: PDF download or shareable link.
- **Google OAuth**: SSO login alongside JWT email/password.

### 4.2 AI & Analysis Pipeline (Remaining)
- **Langfuse Tracing**: Add Langfuse to trace every Gemini API call (prompt, response, latency, tokens) for observability.
- **Stockfish Enhancements**: Principal variation (PV) lines, candidate moves in critical moment coach notes.
- **Report Schema Versioning**: Versioned schema with migration support for future report format changes.
- **RAG Expansion**: Add more chess theory documents; currently 61 passages.

### 4.3 Architecture & Deployment (Remaining)
- **Cloud Storage**: Upload PGN files to GCP Cloud Storage instead of local filesystem.
- **GCP Pub/Sub + Cloud Run Worker**: Replace FastAPI BackgroundTasks with production-grade async job queue for scalability and reliability.
- **Neon DB / PostgreSQL**: Migrate from SQLite to cloud Postgres for production.
- **Dockerization**: `Dockerfile.api`, `Dockerfile.worker`, `docker-compose.yml`.
- **GitHub Actions CI/CD**: Automated test, build, and deploy pipelines.
- **Firebase Hosting**: Deploy React frontend.
- **GCP Secret Manager**: Store API keys at runtime instead of `.env` files.

### 4.4 Frontend Polish (Remaining)
- **Responsive QA**: Mobile layout testing and fixes.
- **Persistent game URLs**: Direct route to `/games/{id}` for shareable links.
- **Critical moment filters**: Filter by blunder / mistake / inaccuracy in the report view.
- **Keyboard controls**: Arrow key navigation in the move replay board.
- **User settings page**: Update display name, change password.

## 5. Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | SQLite path (e.g. `sqlite:///./dev_v2.db`) |
| `UPLOAD_DIR` | Yes | Local dir for PGN uploads (e.g. `uploads`) |
| `STOCKFISH_PATH` | Optional | Path to Stockfish binary |
| `STOCKFISH_DEPTH` | Optional | Analysis depth (default: 12) |
| `STOCKFISH_TIME_LIMIT_SECONDS` | Optional | Per-move time (default: 0.1) |
| `JWT_SECRET_KEY` | Yes (prod) | Secret for signing JWTs |
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `QDRANT_URL` | Yes | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | Yes | Qdrant Cloud API key |
| `QDRANT_COLLECTION` | Optional | Collection name (default: `chess-theory`) |

## 6. Key File Map

```
api/
  main.py              # FastAPI app + router registration
  config.py            # Settings (pydantic-settings, reads .env)
  database.py          # SQLAlchemy engine + Base
  models.py            # SQLAlchemy ORM models (User, Game, MoveEvaluation)
  auth/                # JWT auth: router, dependencies, utils
  games/
    router.py          # All /games endpoints
    service.py         # DB query helpers
    models.py          # Pydantic response schemas
    background.py      # BackgroundTask runner (own DB session)
  users/               # /users/me endpoint
  db/migrations/       # Alembic migration scripts

worker/pipeline/
  orchestrator.py      # Main pipeline: Stockfish → RAG → Gemini
  stockfish_engine.py  # Stockfish UCI integration + fallback evaluator
  rag_retriever.py     # Qdrant similarity search using Gemini embeddings
  llm_coach.py         # GeminiCoach class — builds prompt, calls API, merges report
  report_builder.py    # Deterministic fallback report builder

scripts/
  chess_theory.py      # 61 curated chess theory passage strings
  ingest_theory.py     # One-time ingestion script → Qdrant

frontend/src/
  main.tsx             # App shell, routing, all major components
  api.ts               # All API calls + pollUntilComplete helper
  AuthContext.tsx       # Global auth state + token management
  AuthPages.tsx        # Login + Register UI
  CriticalMomentBoard.tsx  # Chessboard for critical moments
  MoveReplayBoard.tsx      # Move-by-move replay board
  styles.css           # All styles
```
