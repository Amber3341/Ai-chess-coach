import asyncio
import io
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import chess
import chess.engine
import chess.pgn

from api.config import get_settings
from api.games.pgn import normalize_pgn_text


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}


@dataclass(frozen=True)
class MoveEvaluationResult:
    ply: int
    san: str
    fen: str
    eval_cp: int
    classification: str
    best_move_uci: str | None
    best_move_san: str | None
    # Optimization #4: top-3 moves of the engine's best line for richer LLM context
    best_line_san: tuple[str, ...] = field(default_factory=tuple)
    source: str = "material"
    source_detail: str | None = None


def evaluate_pgn(pgn_text: str) -> list[MoveEvaluationResult]:
    """Evaluate a PGN locally using material balance.

    This is a deterministic material-balance evaluator used as a fallback when
    Stockfish is not available. The module boundary mirrors the Stockfish wrapper.
    """
    game = chess.pgn.read_game(io.StringIO(normalize_pgn_text(pgn_text)))
    if game is None:
        raise ValueError("Cannot analyze an empty PGN.")

    board = game.board()
    evaluations: list[MoveEvaluationResult] = []
    previous_eval = _material_eval_cp(board)

    for ply, move in enumerate(game.mainline_moves(), start=1):
        san = board.san(move)
        board.push(move)
        eval_cp = _material_eval_cp(board)
        delta = eval_cp - previous_eval
        # Optimization #16: phase-aware classification thresholds
        classification = _classify_delta(delta=delta, white_to_move=ply % 2 == 1, ply=ply)
        evaluations.append(
            MoveEvaluationResult(
                ply=ply,
                san=san,
                fen=board.fen(),
                eval_cp=eval_cp,
                classification=classification,
                best_move_uci=None,
                best_move_san=None,
                best_line_san=(),
                source="material",
                source_detail=None,
            )
        )
        previous_eval = eval_cp

    if not evaluations:
        raise ValueError("Cannot analyze a PGN with no playable moves.")

    return evaluations


def evaluate_pgn_with_stockfish(
    pgn_text: str,
    stockfish_path: Path,
    depth: int,
    time_limit_seconds: float,
) -> list[MoveEvaluationResult]:
    _ensure_subprocess_event_loop_policy()
    game = chess.pgn.read_game(io.StringIO(normalize_pgn_text(pgn_text)))
    if game is None:
        raise ValueError("Cannot analyze an empty PGN.")

    board = game.board()
    evaluations: list[MoveEvaluationResult] = []

    with chess.engine.SimpleEngine.popen_uci(str(stockfish_path)) as engine:
        limit = chess.engine.Limit(depth=depth, time=time_limit_seconds)

        # Optimization #5: get pre-move eval in a single analyse call
        pre_info = engine.analyse(board, limit)
        previous_eval = _score_to_cp(pre_info["score"])

        for ply, move in enumerate(game.mainline_moves(), start=1):
            san = board.san(move)

            # Optimization #5 + #4: ONE analyse() call before pushing gives us
            # the best move AND the full PV line — no separate engine.play() needed.
            info = engine.analyse(board, limit)
            pv: list[chess.Move] = info.get("pv") or []
            best_move: Optional[chess.Move] = pv[0] if pv else None
            best_move_uci = best_move.uci() if best_move else None
            best_move_san = board.san(best_move) if best_move else None

            # Capture up to 3 moves of the best line in SAN notation
            best_line_san: list[str] = []
            temp_board = board.copy()
            for pv_move in pv[:3]:
                try:
                    best_line_san.append(temp_board.san(pv_move))
                    temp_board.push(pv_move)
                except Exception:
                    break

            board.push(move)

            # Post-move eval — single call
            post_info = engine.analyse(board, limit)
            eval_cp = _score_to_cp(post_info["score"])

            delta = eval_cp - previous_eval
            # Optimization #16: phase-aware thresholds
            classification = _classify_delta(delta=delta, white_to_move=ply % 2 == 1, ply=ply)

            evaluations.append(
                MoveEvaluationResult(
                    ply=ply,
                    san=san,
                    fen=board.fen(),
                    eval_cp=eval_cp,
                    classification=classification,
                    best_move_uci=best_move_uci,
                    best_move_san=best_move_san,
                    best_line_san=tuple(best_line_san),
                    source="stockfish",
                    source_detail=str(stockfish_path),
                )
            )
            previous_eval = eval_cp

    if not evaluations:
        raise ValueError("Cannot analyze a PGN with no playable moves.")

    return evaluations


def evaluate_pgn_auto(pgn_text: str) -> list[MoveEvaluationResult]:
    settings = get_settings()

    # Use path from settings, or fallback to the Docker default
    stockfish_path = settings.stockfish_path or Path("/usr/games/stockfish")

    if stockfish_path.exists():
        try:
            return evaluate_pgn_with_stockfish(
                pgn_text=pgn_text,
                stockfish_path=stockfish_path,
                depth=settings.stockfish_depth,
                time_limit_seconds=settings.stockfish_time_limit_seconds,
            )
        except Exception as exc:
            return _with_source_detail(
                evaluate_pgn(pgn_text),
                f"Stockfish failed, used material fallback: {exc!r}",
            )

    detail = (
        "STOCKFISH_PATH is not configured."
        if settings.stockfish_path is None
        else f"STOCKFISH_PATH does not exist: {settings.stockfish_path}"
    )
    return _with_source_detail(evaluate_pgn(pgn_text), detail)


def _with_source_detail(
    evaluations: list[MoveEvaluationResult],
    source_detail: str,
) -> list[MoveEvaluationResult]:
    return [
        MoveEvaluationResult(
            ply=item.ply,
            san=item.san,
            fen=item.fen,
            eval_cp=item.eval_cp,
            classification=item.classification,
            best_move_uci=item.best_move_uci,
            best_move_san=item.best_move_san,
            best_line_san=item.best_line_san,
            source=item.source,
            source_detail=source_detail,
        )
        for item in evaluations
    ]


def _ensure_subprocess_event_loop_policy() -> None:
    if sys.platform != "win32" or not hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
        return

    policy = asyncio.get_event_loop_policy()
    if not isinstance(policy, asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def _score_to_cp(score: chess.engine.PovScore) -> int:
    """Convert a PovScore (from White's perspective) to centipawns."""
    white_score = score.white()
    if white_score.is_mate():
        mate = white_score.mate()
        if mate is None:
            return 0
        return 100_000 if mate > 0 else -100_000
    return white_score.score(mate_score=100_000) or 0


def _material_eval_cp(board: chess.Board) -> int:
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score


def _classify_delta(delta: int, white_to_move: bool, ply: int = 0) -> str:
    """Classify a move's evaluation delta.

    Optimization #16: endgame positions use tighter thresholds because small
    centipawn swings are often decisive when material is scarce.
    """
    player_delta = delta if white_to_move else -delta
    loss = -player_delta

    move_number = (ply + 1) // 2
    is_endgame = move_number > 35

    blunder_threshold = 150 if is_endgame else 200
    mistake_threshold = 40 if is_endgame else 50
    inaccuracy_threshold = 15 if is_endgame else 20

    if loss >= blunder_threshold:
        return "blunder"
    if loss >= mistake_threshold:
        return "mistake"
    if loss >= inaccuracy_threshold:
        return "inaccuracy"
    return "ok"
