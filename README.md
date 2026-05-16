# ChessMentor AI

AI-powered chess coaching platform based on the PRD, HLD, LLD, and UI wireframe documents in this repository.

## Current Development Milestone

ChessMentor AI is currently at the local MVP stage. The app supports uploading a
single PGN, validating and storing it, running local analysis, generating a
coaching report, and viewing the result in a React workspace.

## Implemented

### Backend API

- FastAPI application with health check, CORS setup, and `/api/v1` game routes.
- SQLite-backed SQLAlchemy models for uploaded games and per-move evaluations.
- `.pgn` upload endpoint with UTF-8 validation, file extension checks, PGN
  parsing through `python-chess`, blank-line normalization, and an MVP limit of
  150 moves.
- Game metadata persistence including players, result, move count, status,
  issue counts, report summary, full report JSON, and analysis errors.
- Local analysis trigger endpoint that moves games through `pending`,
  `processing`, `complete`, and `failed` states.
- Report and move-list read endpoints for completed games.
- Automated tests for health checks, valid PGN upload, blank-line PGN handling,
  report readiness, local analysis, move persistence, and evaluator fallback.

### Analysis Pipeline

- Stockfish integration point using `python-chess` UCI engine calls when
  `STOCKFISH_PATH` is configured.
- Deterministic material-balance fallback evaluator for local development when
  Stockfish is unavailable.
- Per-ply evaluation records with SAN, FEN, centipawn evaluation,
  classification, and optional best move.
- Move classification into `ok`, `inaccuracy`, `mistake`, and `blunder`.
- Structured report builder with summary, top critical moments, opening review,
  middlegame review, endgame review, action plan, and report metadata.

### Frontend

- Vite + React + TypeScript single-page app.
- PGN upload workflow with upload/analyze controls and visible workflow status.
- API client for game upload, local analysis, report fetch, and move fetch.
- Game metadata panel with player names, result, and game ID.
- Report dashboard showing blunder, mistake, inaccuracy, and move counts.
- Coaching report view with summary, critical moments, phase reviews, action
  plan, and full move replay.
- Chessboard rendering with `react-chessboard` for critical positions and
  move-by-move replay.
- Clickable move list and replay controls for first, previous, next, and last
  positions.

### Project Assets

- PRD, HLD, LLD, and UI wireframe documents are included in the repository.
- Example PGN file is available for local testing.
- `.env.example`, backend requirements, frontend package files, pytest config,
  and `.gitignore` are present.

## Local Setup

Backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn api.main:app --reload
```

Then open:

- API health: http://127.0.0.1:8000/health
- Swagger docs: http://127.0.0.1:8000/docs

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Then open:

- Web app: http://127.0.0.1:5173

## Initial Endpoints

```text
GET  /health
POST /api/v1/games
GET  /api/v1/games/{game_id}
POST /api/v1/games/{game_id}/analyze
GET  /api/v1/games/{game_id}/report
GET  /api/v1/games/{game_id}/moves
```

## Stockfish

The worker now has a real Stockfish integration point. If `STOCKFISH_PATH` is set
to a local Stockfish executable, analysis uses `python-chess` UCI engine calls.
If it is not set, the app falls back to a deterministic material-balance
evaluator so local development still works.

Example `.env` value on Windows:

```text
STOCKFISH_PATH="C:/tools/stockfish/stockfish-windows-x86-64-avx2.exe"
STOCKFISH_DEPTH=12
STOCKFISH_TIME_LIMIT_SECONDS=0.1
```

## Still To Build

### Product Features

- User accounts, authentication, and authorization.
- Game history/dashboard for browsing previously uploaded games.
- Support for multiple games in one PGN file.
- Richer coaching content, including opening identification, tactical themes,
  endgame labels, and personalized recommendations.
- Exportable reports, such as PDF or shareable links.
- Better loading/progress states for long-running analysis.
- More user-friendly error recovery for failed analysis jobs.

### Analysis Improvements

- Install/download a Stockfish binary and set `STOCKFISH_PATH` in local and
  deployed environments.
- Improve classification logic to compare the played move against the engine's
  best line more directly instead of relying only on evaluation delta.
- Add principal variation, win/draw/loss probability, and multi-line candidate
  move data.
- Tune depth/time settings and add safeguards for very long or malformed games.
- Add a versioned report schema so future report changes can be migrated safely.

### Architecture And Deployment

- Replace the local `/analyze` trigger with Pub/Sub + Cloud Run worker dispatch.
- Add durable object storage for uploaded PGNs instead of local filesystem
  storage.
- Add database migrations with Alembic or a similar migration tool.
- Add production configuration for Postgres, cloud secrets, logging, and
  observability.
- Add CI checks for backend tests, frontend type-checking, linting, and builds.

### Frontend Polish

- Add responsive QA and browser-level regression checks.
- Improve visual states for empty reports, failed jobs, and Stockfish-disabled
  fallback mode.
- Add filters for critical moments and move classifications.
- Add keyboard controls for replay navigation.
- Add a persistent route for directly opening a game by ID.
