import { StrictMode, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  analyzeGame,
  fetchGames,
  fetchMoves,
  fetchReport,
  type Game,
  type GameReport,
  type MoveEvaluation,
  uploadGame,
} from "./api";
import { CriticalMomentBoard } from "./CriticalMomentBoard";
import { MoveReplayBoard } from "./MoveReplayBoard";
import "./styles.css";

type WorkflowState = "idle" | "uploading" | "uploaded" | "analyzing" | "complete" | "failed";
type HistoryFilter = "all" | Game["status"];

const HISTORY_FILTERS: Array<{ label: string; value: HistoryFilter }> = [
  { label: "All", value: "all" },
  { label: "Complete", value: "complete" },
  { label: "Pending", value: "pending" },
  { label: "Failed", value: "failed" },
];

function App() {
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
    void refreshHistory();
  }, []);

  async function refreshHistory() {
    setHistoryLoading(true);
    try {
      setHistory(await fetchGames());
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
      await refreshHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
      setState("failed");
    }
  }

  async function handleAnalyze() {
    if (!game) return;
    setError(null);
    setState("analyzing");
    try {
      const analyzed = await analyzeGame(game.id);
      setGame(analyzed);
      if (analyzed.status === "failed") {
        throw new Error(analyzed.error_message ?? "Analysis failed.");
      }
      const [nextReport, nextMoves] = await Promise.all([
        fetchReport(analyzed.id),
        fetchMoves(analyzed.id),
      ]);
      setReport(nextReport);
      setMoves(nextMoves);
      setState("complete");
      await refreshHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed.");
      setState("failed");
    }
  }

  async function handleSelectGame(nextGame: Game) {
    setError(null);
    setGame(nextGame);
    setReport(null);
    setMoves([]);
    setState(nextGame.status === "complete" ? "analyzing" : "uploaded");

    if (nextGame.status !== "complete") {
      return;
    }

    try {
      const [nextReport, nextMoves] = await Promise.all([
        fetchReport(nextGame.id),
        fetchMoves(nextGame.id),
      ]);
      setReport(nextReport);
      setMoves(nextMoves);
      setState("complete");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load report.");
      setState("failed");
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">ChessMentor AI</p>
          <h1>Game Analysis Workspace</h1>
        </div>
        <div className={`status-pill status-${state}`}>{state}</div>
      </header>

      <section className="workspace-grid">
        <aside className="upload-panel">
          <h2>Upload PGN</h2>
          <label className="drop-zone">
            <input
              type="file"
              accept=".pgn"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
            <span className="drop-icon">+</span>
            <span>{file ? file.name : "Choose a .pgn file"}</span>
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
                onClick={() => void refreshHistory()}
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

          {state === "analyzing" ? (
            <AnalysisLoading />
          ) : report ? (
            <ReportView report={report} moves={moves} />
          ) : (
            <div className="empty-state">
              <h2>No report loaded</h2>
              <p>Upload a PGN and run analysis to generate the first coaching report.</p>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

function AnalysisLoading() {
  return (
    <div className="analysis-loading" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <div>
        <h2>Analyzing game</h2>
        <p>Running engine evaluation and preparing the coaching report.</p>
      </div>
    </div>
  );
}

function ReportView({ report, moves }: { report: GameReport; moves: MoveEvaluation[] }) {
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
        <h2>Summary</h2>
        <p>{report.summary}</p>
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

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
