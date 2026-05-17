# ChessMentor AI

AI-powered chess coaching platform. Upload a PGN, get a personalized coaching report powered by Stockfish + Gemini 2.5 Flash + RAG (Qdrant).

## Current Development Milestone

**Local AI MVP** — the full analysis pipeline is functional end-to-end:
- User registers/logs in → uploads a PGN → clicks Analyze
- Backend runs Stockfish evaluation + RAG retrieval + Gemini 2.5 Flash report generation **asynchronously**
- Frontend polls for completion and renders a full coaching report with interactive chessboard

---

## Implemented

### Authentication & Multi-User Support
- JWT-based registration and login (`/api/v1/auth/register`, `/api/v1/auth/login`)
- All game routes secured and user-scoped (each user only sees their own games)
- `AuthContext` + `ProtectedRoute` in React; auto-redirect on 401
- Login and Register pages with form validation
- Alembic database migrations (`dev_v2.db`)

### Backend API
- FastAPI with health check, CORS, and `/api/v1` prefix
- SQLite + SQLAlchemy + Alembic migrations
- PGN upload with UTF-8 validation, extension check, and 150-move MVP limit
- Game state machine: `pending` → `processing` → `complete` / `failed`
- `POST /api/v1/games/{id}/analyze` returns **202 Accepted immediately** (async)
- Report, moves, and game-list endpoints (all user-scoped)

### AI Analysis Pipeline
- **Stockfish** integration via `python-chess` UCI with material-balance fallback
- **RAG Pipeline**: 61 chess theory passages embedded with Gemini Embeddings API (`gemini-embedding-001`, 3072-dim) and stored in Qdrant Cloud `chess-theory` collection
- **Gemini 2.5 Flash** receives Stockfish data + top-3 RAG passages → generates coaching report (summary, phase reviews, coach notes, action plan)
- Graceful fallback: if Gemini/Qdrant unavailable, falls back to deterministic rule-based report
- `source_detail` in report metadata shows `"Coaching provided by Gemini 2.5 Flash + RAG"` when both are active

### Async Architecture
- `FastAPI BackgroundTasks` runs the full pipeline in a background thread after returning 202
- Background task creates its own SQLAlchemy session (independent of request lifecycle)
- Frontend polls `GET /games/{id}` every 2s with `pollUntilComplete()` until status changes

### Frontend
- `react-router-dom` routing with `ProtectedRoute` guard
- `api.ts` injects `Authorization: Bearer <token>` in all requests
- `pollUntilComplete()` helper with live progress message
- Full coaching report: summary, critical moments with FEN boards, phase reviews, action plan
- Interactive chessboard (`react-chessboard`) for critical positions and move-by-move replay
- Game history sidebar with search and status filters

### Testing
- 7 automated pytest tests covering: health, upload, list, analysis (async), report, moves, fallback
- Test fixture patches `database_url` so background tasks use the test DB

---

## Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Stockfish binary — download from [stockfishchess.org](https://stockfishchess.org/download/)

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — add GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, STOCKFISH_PATH
uvicorn api.main:app --reload
```

Then open:
- API health: http://127.0.0.1:8000/health
- Swagger docs: http://127.0.0.1:8000/docs

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Then open:
- Web app: http://127.0.0.1:5173

### Ingest Chess Theory into Qdrant (one-time)

```powershell
python scripts/ingest_theory.py
```

This embeds 61 chess theory passages using Gemini Embeddings and uploads them to your Qdrant Cloud cluster.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```text
DATABASE_URL="sqlite:///./dev_v2.db"
UPLOAD_DIR="uploads"

# Optional — enables Stockfish engine evaluation
STOCKFISH_PATH="C:/tools/stockfish/stockfish-windows-x86-64-avx2.exe"
STOCKFISH_DEPTH=12
STOCKFISH_TIME_LIMIT_SECONDS=0.1

# Required for AI coaching
GEMINI_API_KEY="your_gemini_api_key"
QDRANT_URL="https://your-cluster.cloud.qdrant.io"
QDRANT_API_KEY="your_qdrant_api_key"

# Required for auth (change in production!)
JWT_SECRET_KEY="your_secret_key"
```

---

## API Endpoints

```text
GET  /health

POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/users/me

GET  /api/v1/games                       → list user's games
POST /api/v1/games                       → upload PGN
GET  /api/v1/games/{game_id}             → get game status
POST /api/v1/games/{game_id}/analyze     → trigger analysis (202 Accepted)
GET  /api/v1/games/{game_id}/report      → get coaching report
GET  /api/v1/games/{game_id}/moves       → get per-move evaluations
```

---

## Still To Build

### Product Features
- Pagination for larger game histories
- Support for multiple games in one PGN file
- Exportable reports (PDF or shareable link)
- Google OAuth SSO login

### AI & Analysis Pipeline
- **Langfuse Tracing**: Trace every Gemini API call for observability
- **Stockfish Enhancements**: Principal variation (PV) lines and candidate moves in coach notes
- **Report Schema Versioning**: Safe migration of future report format changes
- **RAG Expansion**: Ingest more chess theory documents (currently 61 passages)

### Architecture & Deployment
- **Cloud Storage**: Upload PGNs to GCP Cloud Storage (currently local filesystem)
- **GCP Pub/Sub + Cloud Run Worker**: Replace FastAPI BackgroundTasks with a production job queue
- **Neon DB / PostgreSQL**: Migrate from SQLite to cloud Postgres
- **Dockerization**: `Dockerfile.api`, `Dockerfile.worker`, `docker-compose.yml`
- **GitHub Actions CI/CD**: Automated test, build, and deploy pipelines
- **Firebase Hosting**: Deploy React frontend
- **GCP Secret Manager**: Secure API key management at runtime

### Frontend Polish
- Mobile responsive QA
- Persistent game URLs (`/games/{id}`) for shareable links
- Critical moment filters (blunder / mistake / inaccuracy)
- Keyboard arrow key navigation in move replay
- User settings page (display name, password change)
