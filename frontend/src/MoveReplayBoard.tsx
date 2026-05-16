import { useMemo, useState } from "react";
import { Chessboard } from "react-chessboard";
import type { MoveEvaluation } from "./api";

export function MoveReplayBoard({ moves }: { moves: MoveEvaluation[] }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeMove = moves[activeIndex];

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
          <button className="secondary" disabled={activeIndex === 0} onClick={() => setActiveIndex(0)}>
            First
          </button>
          <button
            className="secondary"
            disabled={activeIndex === 0}
            onClick={() => setActiveIndex((index) => Math.max(0, index - 1))}
          >
            Previous
          </button>
          <button
            className="secondary"
            disabled={activeIndex === moves.length - 1}
            onClick={() => setActiveIndex((index) => Math.min(moves.length - 1, index + 1))}
          >
            Next
          </button>
          <button
            className="secondary"
            disabled={activeIndex === moves.length - 1}
            onClick={() => setActiveIndex(moves.length - 1)}
          >
            Last
          </button>
        </div>
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
