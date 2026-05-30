import { StrictMode, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  analyzeGame,
  createShareLink,
  fetchGames,
  fetchGame,
  fetchMoves,
  fetchReport,
  fetchSharedReport,
  pollUntilComplete,
  type Game,
  type GameReport,
  type MoveEvaluation,
  uploadGame,
} from "./api";
import { CriticalMomentBoard } from "./CriticalMomentBoard";
import { MoveReplayBoard } from "./MoveReplayBoard";
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate, useParams } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import { LoginPage, RegisterPage } from "./AuthPages";
import { OAuthCallback } from "./OAuthCallback";
import "./styles.css";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  
  if (loading) return <div style={{ padding: "2rem", textAlign: "center" }}>Loading user data...</div>;
  if (!user) return <Navigate to="/login" replace state={{ from: location }} />;
  
  return <>{children}</>;
}

type WorkflowState = "idle" | "uploading" | "uploaded" | "analyzing" | "complete" | "failed";
type HistoryFilter = "all" | Game["status"];

const HISTORY_FILTERS: Array<{ label: string; value: HistoryFilter }> = [
  { label: "All", value: "all" },
  { label: "Complete", value: "complete" },
  { label: "Pending", value: "pending" },
  { label: "Failed", value: "failed" },
];
const HISTORY_PAGE_SIZE = 10;

function App() {
  const { gameId } = useParams();
  const navigate = useNavigate();
  const failedGameIdRef = useRef<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [game, setGame] = useState<Game | null>(null);
  const [report, setReport] = useState<GameReport | null>(null);
  const [moves, setMoves] = useState<MoveEvaluation[]>([]);
  const [history, setHistory] = useState<Game[]>([]);
  const [state, setState] = useState<WorkflowState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyQuery, setHistoryQuery] = useState("");
  const [historyFilter, setHistoryFilter] = useState<HistoryFilter>("all");
  const [historyPage, setHistoryPage] = useState(1);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyTotalPages, setHistoryTotalPages] = useState(1);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const { user, logout } = useAuth();

  const stats = useMemo(
    () => [
      { label: "Blunders", value: game?.blunders ?? 0, tone: "danger" },
      { label: "Mistakes", value: game?.mistakes ?? 0, tone: "warn" },
      { label: "Inaccuracies", value: game?.inaccuracies ?? 0, tone: "info" },
      { label: "Moves", value: game?.moves ?? 0, tone: "plain" },
    ],
    [game],
  );

  const filteredHistory = useMemo(() => {
    const query = historyQuery.trim().toLowerCase();

    return history.filter((item) => {
      const matchesFilter = historyFilter === "all" || item.status === historyFilter;
      const searchable = [
        item.white_player,
        item.black_player,
        item.result,
        item.status,
        item.id,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return matchesFilter && (!query || searchable.includes(query));
    });
  }, [history, historyFilter, historyQuery]);

  useEffect(() => {
    void refreshHistory(1);
  }, []);

  useEffect(() => {
    if (!gameId) {
      setGame(null);
      setReport(null);
      setMoves([]);
      setState("idle");
      setAnalyzeProgress(null);
      setShareUrl(null);
      return;
    }

    if (failedGameIdRef.current === gameId) {
      return;
    }

    if (game?.id === gameId && state !== "idle") {
      return;
    }

    void loadGameFromRoute(gameId);
  }, [gameId, game?.id, state]);

  async function refreshHistory(page = historyPage) {
    setHistoryLoading(true);
    try {
      const response = await fetchGames(page, HISTORY_PAGE_SIZE);
      setHistory(response.items);
      setHistoryPage(response.page);
      setHistoryTotal(response.total);
      setHistoryTotalPages(response.total_pages);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load game history.");
    } finally {
      setHistoryLoading(false);
    }
  }

  async function handleUpload() {
    if (!file) return;
    setError(null);
    setReport(null);
    setMoves([]);
    setState("uploading");
    try {
      const uploaded = await uploadGame(file);
      setGame(uploaded);
      setState("uploaded");
      navigate(`/games/${uploaded.id}`);
      await refreshHistory(1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
      setState("failed");
    }
  }

  const [analyzeProgress, setAnalyzeProgress] = useState<string | null>(null);

  async function handleAnalyze() {
    if (!game) return;
    setError(null);
    setAnalyzeProgress("Starting analysis...");
    setState("analyzing");
    try {
      // Trigger analysis — returns 202 immediately with status="processing"
      const triggered = await analyzeGame(game.id);
      setGame(triggered);
      navigate(`/games/${triggered.id}`);
      setAnalyzeProgress(null);

      // Poll every 2s until the background job finishes
      const completed = await pollUntilComplete(
        game.id,
        (polled) => setGame(polled),
      );

      setAnalyzeProgress(null);
      if (completed.status === "failed") {
        throw new Error(completed.error_message ?? "Analysis failed.");
      }

      const [nextReport, nextMoves] = await Promise.all([
        fetchReport(completed.id),
        fetchMoves(completed.id),
      ]);
      setReport(nextReport);
      setMoves(nextMoves);
      setState("complete");
      await refreshHistory(historyPage);
    } catch (err) {
      setAnalyzeProgress(null);
      setError(err instanceof Error ? err.message : "Analysis failed.");
      setState("failed");
    }
  }

  async function handleSelectGame(nextGame: Game) {
    if (nextGame.id === gameId) {
      await loadGameDetails(nextGame);
      return;
    }

    navigate(`/games/${nextGame.id}`);
  }

  async function loadGameFromRoute(id: string) {
    try {
      failedGameIdRef.current = null;
      const nextGame = await fetchGame(id);
      await loadGameDetails(nextGame);
    } catch (err) {
      failedGameIdRef.current = id;
      setGame(null);
      setReport(null);
      setMoves([]);
      setState("failed");
      setAnalyzeProgress(null);
      setError(err instanceof Error ? err.message : "Could not load game.");
    }
  }

  async function loadGameDetails(nextGame: Game) {
    failedGameIdRef.current = null;
    setError(null);
    setGame(nextGame);
    setReport(null);
    setMoves([]);
    setShareUrl(null);
    setAnalyzeProgress(null);

    if (nextGame.status === "failed") {
      setState("failed");
      setError(nextGame.error_message ?? "Analysis failed.");
      return;
    }

    if (nextGame.status === "processing") {
      setState("analyzing");
      setAnalyzeProgress("Analysis is still running...");
      try {
        const completed = await pollUntilComplete(
          nextGame.id,
          (polled) => setGame(polled),
        );

        setAnalyzeProgress(null);
        if (completed.status === "failed") {
          throw new Error(completed.error_message ?? "Analysis failed.");
        }

        await loadGameDetails(completed);
        return;
      } catch (err) {
        setAnalyzeProgress(null);
        setError(err instanceof Error ? err.message : "Analysis failed.");
        setState("failed");
        return;
      }
    }

    if (nextGame.status !== "complete") {
      setState("uploaded");
      return;
    }

    setState("analyzing");
    setAnalyzeProgress("Loading saved report...");
    try {
      const [nextReport, nextMoves] = await Promise.all([
        fetchReport(nextGame.id),
        fetchMoves(nextGame.id),
      ]);
      setReport(nextReport);
      setMoves(nextMoves);
      setState("complete");
      setAnalyzeProgress(null);
    } catch (err) {
      setAnalyzeProgress(null);
      setError(err instanceof Error ? err.message : "Could not load report.");
      setState("failed");
    }
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  }

  function resetWorkspace() {
    setGame(null);
    setReport(null);
    setMoves([]);
    setState("idle");
    setFile(null);
    setError(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">ChessMentor AI</p>
          <h1>Game Analysis Workspace</h1>
        </div>
        <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
          <span>{user?.display_name || user?.email}</span>
          <button className="secondary" onClick={() => setShowLogoutModal(true)}>Log Out</button>
          <div className={`status-pill status-${state}`}>{state}</div>
        </div>
      </header>

      <section className="workspace-grid">
        <aside className="upload-panel">
          <h2>Upload PGN</h2>
          <label 
            className={`drop-zone ${isDragging ? "is-dragging" : ""}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pgn"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
            <span className="drop-icon">+</span>
            <span>{file ? file.name : "Drag & drop or Choose a .pgn file"}</span>
          </label>

          <div className="button-row">
            <button disabled={!file || state === "uploading"} onClick={handleUpload}>
              {state === "uploading" ? "Uploading" : "Upload"}
            </button>
            <button
              className="secondary"
              disabled={!game || state === "uploading" || state === "analyzing"}
              onClick={handleAnalyze}
            >
              {state === "analyzing" ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {error ? <p className="error-banner">{error}</p> : null}

          {game ? (
            <dl className="game-meta">
              <div>
                <dt>White</dt>
                <dd>{game.white_player ?? "Unknown"}</dd>
              </div>
              <div>
                <dt>Black</dt>
                <dd>{game.black_player ?? "Unknown"}</dd>
              </div>
              <div>
                <dt>Result</dt>
                <dd>{game.result ?? "Unknown"}</dd>
              </div>
              <div>
                <dt>Game ID</dt>
                <dd className="mono">{game.id}</dd>
              </div>
            </dl>
          ) : null}

          <section className="history-panel">
            <div className="history-heading">
              <h2>Recent Games</h2>
              <button
                className="icon-button"
                disabled={historyLoading}
                onClick={() => void refreshHistory(historyPage)}
                title="Refresh game history"
              >
                Refresh
              </button>
            </div>

            <input
              className="history-search"
              type="search"
              placeholder="Search players or ID"
              value={historyQuery}
              onChange={(event) => setHistoryQuery(event.target.value)}
            />

            <div className="history-filters" aria-label="History filters">
              {HISTORY_FILTERS.map((filter) => (
                <button
                  className={historyFilter === filter.value ? "is-active" : ""}
                  key={filter.value}
                  onClick={() => setHistoryFilter(filter.value)}
                >
                  {filter.label}
                </button>
              ))}
            </div>

            {filteredHistory.length > 0 ? (
              <div className="history-list">
                {filteredHistory.map((item) => (
                  <button
                    className={`history-item ${game?.id === item.id ? "is-active" : ""}`}
                    key={item.id}
                    onClick={() => void handleSelectGame(item)}
                  >
                    <span>{item.white_player ?? "White"} vs {item.black_player ?? "Black"}</span>
                    <strong>{item.status}</strong>
                    <em>{item.result ?? "Unknown"} - {item.moves ?? 0} moves</em>
                  </button>
                ))}
              </div>
            ) : (
              <p className="history-empty">
                {historyLoading ? "Loading games..." : "No matching games."}
              </p>
            )}

            <div className="history-pagination">
              <button
                className="secondary"
                disabled={historyLoading || historyPage <= 1}
                onClick={() => void refreshHistory(historyPage - 1)}
              >
                Previous
              </button>
      <span>
                Page {historyPage} / {historyTotalPages} - {historyTotal} games
              </span>
              <button
                className="secondary"
                disabled={historyLoading || historyPage >= historyTotalPages}
                onClick={() => void refreshHistory(historyPage + 1)}
              >
                Next
              </button>
            </div>
          </section>
        </aside>

        <section className="report-panel">
          <div className="stat-grid">
            {stats.map((item) => (
              <div className={`stat stat-${item.tone}`} key={item.label}>
                <span>{item.label}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>

          {state === "uploading" ? (
            <div className="analysis-loading" role="status" aria-live="polite">
              <div className="spinner" aria-hidden="true" />
              <div>
                <h2>Uploading PGN...</h2>
                <p>Please wait while your file is uploaded and parsed.</p>
              </div>
            </div>
          ) : state === "analyzing" ? (
            <AnalysisLoading message={analyzeProgress} />
          ) : state === "failed" ? (
            <div className="empty-state">
              <h2>Action Failed</h2>
              <p>{error || "An error occurred during upload or analysis."}</p>
            </div>
          ) : report ? (
            <ReportView
              report={report}
              moves={moves}
              shareUrl={shareUrl}
              onShare={game ? () => void handleCreateShareLink(game.id) : undefined}
              onReset={resetWorkspace}
            />
          ) : (
            <div className="empty-state">
              <h2>No report loaded</h2>
              <p>Upload a PGN and run analysis to generate the first coaching report.</p>
            </div>
          )}
        </section>
      </section>

      {showLogoutModal ? (
        <div className="modal-overlay">
          <div className="modal-content" role="dialog" aria-modal="true">
            <h2>Log Out</h2>
            <p>Are you sure you want to log out of your account?</p>
            <div className="modal-actions">
              <button className="secondary" onClick={() => setShowLogoutModal(false)}>Cancel</button>
              <button onClick={() => {
                setShowLogoutModal(false);
                logout();
              }}>Log Out</button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );

  async function handleCreateShareLink(gameId: string) {
    setError(null);
    try {
      const response = await createShareLink(gameId);
      const absoluteUrl = new URL(response.share_url, window.location.origin).toString();
      setShareUrl(absoluteUrl);
      await navigator.clipboard?.writeText(absoluteUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create share link.");
    }
  }
}

function AnalysisLoading({ message }: { message?: string | null }) {
  const [step, setStep] = useState(0);
  
  const steps = useMemo(() => [
    "Evaluating Opening lines...",
    "Scanning for blunders...",
    "Analyzing middlegame tactics...",
    "Reviewing endgame technique...",
    "Writing personalized coaching notes...",
    "Finalizing report..."
  ], []);

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((s) => (s + 1) % steps.length);
    }, 6000);
    return () => clearInterval(interval);
  }, [steps.length]);

  return (
    <div className="analysis-loading" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <div>
        <h2>Analyzing game</h2>
        <p>{message ?? steps[step]}</p>
      </div>
    </div>
  );
}

function ReportView({
  report,
  moves,
  shareUrl,
  onShare,
  onReset,
}: {
  report: GameReport;
  moves: MoveEvaluation[];
  shareUrl?: string | null;
  onShare?: () => void;
  onReset?: () => void;
}) {
  const isFallbackReport = report.metadata.source === "material";

  return (
    <div className="report-view">
      {isFallbackReport ? (
        <section className="report-notice">
          <strong>Fallback analysis used</strong>
          <p>
            Stockfish was unavailable for this run, so the report was generated
            with the local material evaluator.
          </p>
          {report.metadata.source_detail ? (
            <code>{report.metadata.source_detail}</code>
          ) : null}
        </section>
      ) : null}

      <section className="report-section">
        <div className="report-section-heading">
          <h2>Summary</h2>
          <div style={{ display: "flex", gap: "1rem" }}>
            {onReset ? (
              <button className="primary" onClick={onReset}>
                Analyze Another Game
              </button>
            ) : null}
            {onShare ? (
              <button className="secondary" onClick={onShare}>
                Share Report
              </button>
            ) : null}
          </div>
        </div>
        <p>{report.summary}</p>
        {shareUrl ? (
          <div className="share-link-box">
            <span>Public share link copied</span>
            <code>{shareUrl}</code>
          </div>
        ) : null}
      </section>

      <section className="report-section">
        <h2>Critical Moments</h2>
        <CriticalMomentBoard moments={report.critical_moments} />
      </section>

      <section className="phase-grid">
        <Phase title="Opening" text={report.opening_review} />
        <Phase title="Middlegame" text={report.middlegame_review} />
        <Phase title="Endgame" text={report.endgame_review} />
      </section>

      <section className="report-section">
        <h2>Action Plan</h2>
        <ul className="action-list">
          {report.action_plan.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="report-section">
        <h2>Full Move Replay</h2>
        <MoveReplayBoard moves={moves} />
      </section>
    </div>
  );
}

function Phase({ title, text }: { title: string; text: string }) {
  return (
    <section className="phase">
      <h2>{title}</h2>
      <p>{text}</p>
    </section>
  );
}

function SharedReportPage() {
  const { shareToken } = useParams();
  const [report, setReport] = useState<GameReport | null>(null);
  const [moves, setMoves] = useState<MoveEvaluation[]>([]);
  const [game, setGame] = useState<Game | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!shareToken) return;
    const token = shareToken;
    async function loadSharedReport() {
      try {
        const response = await fetchSharedReport(token);
        setGame(response.game);
        setReport(response.report);
        setMoves(response.moves);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Could not load shared report.");
      }
    }

    void loadSharedReport();
  }, [shareToken]);

  return (
    <main className="app-shell shared-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">ChessMentor AI</p>
          <h1>Shared Coaching Report</h1>
        </div>
      </header>

      {error ? <p className="error-banner">{error}</p> : null}

      {game && report ? (
        <section className="report-panel">
          <div className="shared-game-heading">
            <h2>
              {game.white_player ?? "White"} vs {game.black_player ?? "Black"}
            </h2>
            <span className="status-pill status-complete">{game.result ?? "Result unknown"}</span>
          </div>
          <ReportView report={report} moves={moves} />
        </section>
      ) : !error ? (
        <div className="empty-state">
          <h2>Loading shared report</h2>
          <p>Fetching the public coaching report.</p>
        </div>
      ) : null}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/oauth-callback" element={<OAuthCallback />} />
          <Route path="/shared/:shareToken" element={<SharedReportPage />} />
          <Route path="/" element={
            <ProtectedRoute>
              <App />
            </ProtectedRoute>
          } />
          <Route path="/games/:gameId" element={
            <ProtectedRoute>
              <App />
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>
);
