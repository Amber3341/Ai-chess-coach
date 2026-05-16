import { useMemo, useState } from "react";
import { Chessboard } from "react-chessboard";
import type { GameReport } from "./api";

type CriticalMoment = GameReport["critical_moments"][number];

export function CriticalMomentBoard({ moments }: { moments: CriticalMoment[] }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeMoment = moments[activeIndex];

  const boardOptions = useMemo(
    () => ({
      id: "critical-moment-board",
      position: activeMoment?.fen ?? "start",
      allowDragging: false,
      showAnimations: true,
      animationDurationInMs: 180,
      boardStyle: {
        borderRadius: "8px",
        boxShadow: "0 10px 24px rgba(24, 32, 47, 0.18)",
        overflow: "hidden",
      },
      lightSquareStyle: { backgroundColor: "#eff4f7" },
      darkSquareStyle: { backgroundColor: "#31516f" },
    }),
    [activeMoment?.fen],
  );

  if (!activeMoment) {
    return (
      <section className="board-panel">
        <div className="board-empty">No critical positions found.</div>
      </section>
    );
  }

  return (
    <section className="board-panel">
      <div className="board-stage">
        <Chessboard options={boardOptions} />
      </div>

      <div className="board-copy">
        <div className="board-heading">
          <span className={`badge badge-${activeMoment.classification}`}>
            {activeMoment.classification}
          </span>
          <div>
            <h2>
              Move {activeMoment.move_number}: {activeMoment.san}
            </h2>
            <p>
              {activeMoment.side} to move result - Eval{" "}
              {(activeMoment.eval_cp / 100).toFixed(2)}
            </p>
          </div>
        </div>

        <p>{activeMoment.coach_note}</p>
        <div className="best-move-callout">
          <span>Best move</span>
          <strong>
            {activeMoment.best_move_san ?? activeMoment.best_move_uci ?? "Not available"}
          </strong>
        </div>
        <code>{activeMoment.fen}</code>

        <div className="board-controls">
          <button
            className="secondary"
            disabled={activeIndex === 0}
            onClick={() => setActiveIndex((index) => Math.max(0, index - 1))}
          >
            Previous
          </button>
          <span>
            {activeIndex + 1} / {moments.length}
          </span>
          <button
            className="secondary"
            disabled={activeIndex === moments.length - 1}
            onClick={() =>
              setActiveIndex((index) => Math.min(moments.length - 1, index + 1))
            }
          >
            Next
          </button>
        </div>
      </div>
    </section>
  );
}
