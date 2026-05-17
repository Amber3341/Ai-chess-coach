import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Chessboard } from "react-chessboard";
import type { MoveEvaluation } from "./api";

export function MoveReplayBoard({ moves }: { moves: MoveEvaluation[] }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeMove = moves[activeIndex];
  const activeMoveRef = useRef<HTMLButtonElement | null>(null);

  const goNext = useCallback(() =>
    setActiveIndex((i) => Math.min(moves.length - 1, i + 1)), [moves.length]);
  const goPrev = useCallback(() =>
    setActiveIndex((i) => Math.max(0, i - 1)), []);
  const goFirst = useCallback(() => setActiveIndex(0), []);
  const goLast = useCallback(() => setActiveIndex(moves.length - 1), [moves.length]);

  // ← → Home End keyboard navigation
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      // Only handle if no input/textarea is focused
      if (
        document.activeElement instanceof HTMLInputElement ||
        document.activeElement instanceof HTMLTextAreaElement
      ) return;

      if (e.key === "ArrowRight") { e.preventDefault(); goNext(); }
      if (e.key === "ArrowLeft")  { e.preventDefault(); goPrev(); }
      if (e.key === "Home")       { e.preventDefault(); goFirst(); }
      if (e.key === "End")        { e.preventDefault(); goLast(); }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [goNext, goPrev, goFirst, goLast]);

  // Auto-scroll active move into view in the move list
  useEffect(() => {
    activeMoveRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [activeIndex]);

  const boardOptions = useMemo(
    () => ({
      id: "move-replay-board",
      position: activeMove?.fen ?? "start",
      allowDragging: false,
      showAnimations: true,
      animationDurationInMs: 120,
      boardStyle: {
        borderRadius: "8px",
        boxShadow: "0 10px 24px rgba(24, 32, 47, 0.18)",
        overflow: "hidden",
      },
      lightSquareStyle: { backgroundColor: "#eff4f7" },
      darkSquareStyle: { backgroundColor: "#31516f" },
    }),
    [activeMove?.fen],
  );

  if (moves.length === 0) {
    return <div className="board-empty">No move evaluations available.</div>;
  }

  return (
    <div className="replay-grid">
      <div className="replay-board-column">
        <div className="board-stage">
          <Chessboard options={boardOptions} />
        </div>

        <div className="replay-controls">
          <button className="secondary" disabled={activeIndex === 0} onClick={goFirst} title="First move (Home)">
            ⏮ First
          </button>
          <button
            className="secondary"
            disabled={activeIndex === 0}
            onClick={goPrev}
            title="Previous move (←)"
          >
            ◀ Prev
          </button>
          <button
            className="secondary"
            disabled={activeIndex === moves.length - 1}
            onClick={goNext}
            title="Next move (→)"
          >
            Next ▶
          </button>
          <button
            className="secondary"
            disabled={activeIndex === moves.length - 1}
            onClick={goLast}
            title="Last move (End)"
          >
            Last ⏭
          </button>
        </div>
        <p className="keyboard-hint">← → arrow keys to navigate · Home / End to jump</p>
      </div>

      <div className="replay-side">
        <div className="replay-current">
          <span className={`badge badge-${activeMove.classification}`}>
            {activeMove.classification}
          </span>
          <div>
            <h3>
              Ply {activeMove.ply}: {activeMove.san}
            </h3>
            <p>Eval {(activeMove.eval_cp / 100).toFixed(2)}</p>
            <p>
              Best: {activeMove.best_move_san ?? activeMove.best_move_uci ?? "Not available"}
            </p>
          </div>
        </div>

        <div className="move-list" aria-label="Move list">
          {moves.map((move, index) => (
            <button
              ref={index === activeIndex ? activeMoveRef : null}
              className={`move-list-item ${index === activeIndex ? "is-active" : ""} move-${move.classification}`}
              key={`${move.ply}-${move.san}`}
              onClick={() => setActiveIndex(index)}
            >
              <span>{move.ply}</span>
              <strong>{move.san}</strong>
              <em>
                {(move.eval_cp / 100).toFixed(2)}
                {move.best_move_san ? ` · ${move.best_move_san}` : ""}
              </em>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
