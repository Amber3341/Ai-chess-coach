# ChessMentor AI

AI-powered chess coaching platform. Upload a PGN, run analysis, and get a personalized coaching report powered by Stockfish, Gemini 2.5 Flash, and RAG over Qdrant chess theory passages.

## Current Development Milestone

**Cloud-connected MVP** - the core product flow is functional end-to-end:

- User registers/logs in -> uploads a PGN -> clicks Analyze
- Backend saves PGNs to GCS when configured and stores game data in SQLite or Postgres
- Analysis jobs publish to GCP Pub/Sub when configured, with local BackgroundTasks fallback
- Worker pipeline runs Stockfish evaluation + RAG retrieval + Gemini 2.5 Flash report generation
- Frontend polls for completion and renders a full coaching report with interactive chessboards

---

## Implemented

### Authentication & Multi-User Support

- JWT-based registration and login (`/api/v1/auth/register`, `/api/v1/auth/login`)
- Google OAuth SSO login (`/api/v1/auth/google`, `/api/v1/auth/google/callback`)
- All game routes secured and user-scoped
- `AuthContext` + `ProtectedRoute` in React
- Auto-redirect on `401 Unauthorized`
- Login and Register pages with form validation and Google Sign-In buttons
- Login/Register return users to the originally requested protected route

### Backend API

- FastAPI with health check, CORS, and `/api/v1` prefix
- SQLite/Postgres-compatible SQLAlchemy setup with Alembic migrations
- PGN upload with UTF-8 validation, extension check, and 150-move MVP limit
- Game state machine: `pending` -> `processing` -> `complete` / `failed`
- `POST /api/v1/games/{id}/analyze` returns `202 Accepted` immediately
- Report, moves, and game-list endpoints, all user-scoped
- Optional GCS-backed PGN storage with local filesystem fallback

### AI Analysis Pipeline

- Stockfish integration via `python-chess` UCI with material-balance fallback
- RAG pipeline using Gemini Embeddings (`gemini-embedding-001`) and Qdrant Cloud
- 61 curated chess theory passages in the `chess-theory` collection
- Gemini 2.5 Flash coaching report generation
- Deterministic fallback report if Gemini or Qdrant is unavailable
- Gemini retry handling for temporary `503` / unavailable errors before fallback
- `source_detail` metadata explains whether Gemini/RAG or fallback reporting was used

### Async & Cloud Architecture

- GCP Pub/Sub job dispatch for analysis requests
- Pub/Sub push endpoint: `POST /api/v1/internal/pubsub/analyze`
- Cloud Run-compatible backend container via `Dockerfile`
- Local fallback using FastAPI `BackgroundTasks`
- Background tasks create their own SQLAlchemy session independent of request lifecycle
- Cloud Run logs include Pub/Sub publish, push receipt, worker completion, and worker failure breadcrumbs

### Frontend

- React + Vite + TypeScript app
- `react-router-dom` routing with `ProtectedRoute`
- Persistent game URLs via `/games/{id}` for refreshable/shareable report pages
- `api.ts` injects `Authorization: Bearer <token>` in all API requests
- `pollUntilComplete()` polls game status until analysis finishes
- Full coaching report: summary, critical moments, phase reviews, action plan, and move replay
- Interactive chessboards via `react-chessboard`
- Critical moment filters for blunder / mistake / inaccuracy
- Keyboard arrow key navigation for move replay
- Game history sidebar with search and status filters
- Paginated game history API and Previous/Next controls in the sidebar
- Public share links for completed reports via `/shared/{token}`

### Testing & Test Assets

- 9 automated pytest tests covering health, upload, paginated list, analysis, report, moves, sharing, and fallback
- Test fixture patches `database_url` so background tasks use the test DB
- Frontend production build verified with `npm run build`
- Example PGN files are available in `test-pgns/`

---

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Optional: Stockfish binary from <https://stockfishchess.org/download/>

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env with DATABASE_URL, JWT_SECRET_KEY, GEMINI_API_KEY, QDRANT_URL, QDRANT_API_KEY, and optional STOCKFISH_PATH
uvicorn api.main:app --reload
```

Then open:

- API health: <http://127.0.0.1:8000/health>
- Swagger docs: <http://127.0.0.1:8000/docs>

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Then open:

- Web app: <http://127.0.0.1:5173>

### Ingest Chess Theory into Qdrant

```powershell
python scripts/ingest_theory.py
```

This embeds 61 chess theory passages using Gemini Embeddings and uploads them to the configured Qdrant collection.

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```text
APP_NAME="ChessMentor AI"
API_PREFIX="/api/v1"
DATABASE_URL="sqlite:///./dev_v2.db"
UPLOAD_DIR="uploads"
CORS_ORIGINS="http://127.0.0.1:5173,http://localhost:5173"

# Optional local/Docker Stockfish settings
STOCKFISH_PATH="C:/tools/stockfish/stockfish-windows-x86-64-avx2.exe"
STOCKFISH_DEPTH=12
STOCKFISH_TIME_LIMIT_SECONDS=0.1

# Auth
JWT_SECRET_KEY="your_secret_key"
GOOGLE_CLIENT_ID="your_google_client_id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
FRONTEND_URL="http://localhost:5173"

# AI coaching
GEMINI_API_KEY="your_gemini_api_key"
QDRANT_URL="https://your-cluster.cloud.qdrant.io"
QDRANT_API_KEY="your_qdrant_api_key"
QDRANT_COLLECTION="chess-theory"

# Optional cloud deployment
GCP_PROJECT_ID="your-gcp-project-id"
GCS_BUCKET_NAME="your-gcs-bucket"
GCP_PUBSUB_TOPIC_ID="your-pubsub-topic"
```

For the deployed frontend, set:

```text
VITE_API_BASE_URL="https://your-cloud-run-service-url"
```

---

## API Endpoints

```text
GET  /health

POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/google
GET  /api/v1/auth/google/callback
GET  /api/v1/users/me

GET  /api/v1/games?page=1&page_size=10
POST /api/v1/games
GET  /api/v1/games/{game_id}
POST /api/v1/games/{game_id}/analyze
GET  /api/v1/games/{game_id}/report
GET  /api/v1/games/{game_id}/moves
POST /api/v1/games/{game_id}/share
GET  /api/v1/games/shared/{share_token}

POST /api/v1/internal/pubsub/analyze
```

---

## Cloud Verification

Useful Cloud Run log searches:

```text
Published analysis job for game_id
Received Pub/Sub push for game_id
Completed Pub/Sub analysis for game_id
Worker pipeline completed
Worker pipeline failed
Gemini LLM skipped
```

Redeploy backend without losing Cloud Run env vars:

```powershell
gcloud.cmd run deploy chessmentor-api `
  --source . `
  --region asia-south1 `
  --project project-4254caeb-2f7e-4a20-899
```

Avoid `--set-env-vars` during redeploy unless you include every variable. Use `--update-env-vars` for targeted changes.

---

## Still To Build

### Product Features

- Support for multiple games in one PGN file
- Exportable reports as PDF
- User settings page for display name and password changes

### AI & Analysis Pipeline

- Langfuse tracing for Gemini calls, latency, prompt/response metadata, and token usage
- Stockfish enhancements: principal variation lines and richer candidate move suggestions
- Report schema versioning for future report migrations
- RAG expansion beyond the current 61 theory passages

### Architecture & Deployment

- Firebase Hosting deployment for the React frontend
- Add final Firebase Hosting URL to backend `CORS_ORIGINS`
- GitHub Actions CI/CD for backend tests, frontend build, and deploys
- Move secrets from plain Cloud Run env vars to GCP Secret Manager
- Replace public Cloud Run invoker access with OIDC-authenticated Pub/Sub push

### Frontend Polish

- Mobile responsive QA across phone/tablet/desktop breakpoints
- Visual polish for loading, empty, failed, and fallback report states
- Better report source/status display when Gemini fallback is used

---

## Completed From Earlier Roadmap

- Cloud Storage-backed PGN uploads with local fallback
- GCP Pub/Sub job dispatch with Cloud Run push endpoint
- Neon/Postgres-compatible database URL support
- Dockerfile and Docker Compose baseline
- Persistent game URLs (`/games/{id}`)
- Critical moment filters
- Keyboard arrow key navigation in move replay
