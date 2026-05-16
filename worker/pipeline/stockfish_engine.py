import asyncio
import io
import sys
from dataclasses import dataclass
from pathlib import Path

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
    source: str = "material"
    source_detail: str | None = None


def evaluate_pgn(pgn_text: str) -> list[MoveEvaluationResult]:
    """Evaluate a PGN locally.

    This is a deterministic material-balance evaluator used while the app is
    still local-only. The module boundary mirrors the future Stockfish wrapper.
    """
    game = chess.pgn.read_game(io.StringIO(normalize_pgn_text(pgn_text)))
    if game is None:
        raise ValueError("Cannot analyze an empty PGN.")

    board = game.board()
    evaluations: list[MoveEvaluationResult] = []
    previous_eval = _material_eval_cp(board)

    for ply, move in enumerate(game.mainline_moves(), start=1):
        san = board.san(move)
        best_move_uci = None
        best_move_san = None
        board.push(move)
        eval_cp = _material_eval_cp(board)
        delta = eval_cp - previous_eval
        classification = _classify_delta(delta=delta, white_to_move=ply % 2 == 1)
        evaluations.append(
            MoveEvaluationResult(
                ply=ply,
                san=san,
                fen=board.fen(),
                eval_cp=eval_cp,
                classification=classification,
                best_move_uci=best_move_uci,
                best_move_san=best_move_san,
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
        previous_eval = _engine_eval_cp(engine, board, depth, time_limit_seconds)
        for ply, move in enumerate(game.mainline_moves(), start=1):
            san = board.san(move)
            best_move = _engine_best_move(engine, board, depth, time_limit_seconds)
            best_move_uci = best_move.uci() if best_move else None
            best_move_san = board.san(best_move) if best_move else None
            board.push(move)
            eval_cp = _engine_eval_cp(engine, board, depth, time_limit_seconds)
            delta = eval_cp - previous_eval
            classification = _classify_delta(delta=delta, white_to_move=ply % 2 == 1)
            evaluations.append(
                MoveEvaluationResult(
                    ply=ply,
                    san=san,
                    fen=board.fen(),
                    eval_cp=eval_cp,
                    classification=classification,
                    best_move_uci=best_move_uci,
                    best_move_san=best_move_san,
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
    if settings.stockfish_path and settings.stockfish_path.exists():
        try:
            return evaluate_pgn_with_stockfish(
                pgn_text=pgn_text,
                stockfish_path=settings.stockfish_path,
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


def _engine_eval_cp(
    engine: chess.engine.SimpleEngine,
    board: chess.Board,
    depth: int,
    time_limit_seconds: float,
) -> int:
    limit = chess.engine.Limit(depth=depth, time=time_limit_seconds)
    info = engine.analyse(board, limit)
    score = info["score"].white()

    if score.is_mate():
        mate = score.mate()
        if mate is None:
            return 0
        return 100000 if mate > 0 else -100000

    return score.score(mate_score=100000) or 0


def _engine_best_move(
    engine: chess.engine.SimpleEngine,
    board: chess.Board,
    depth: int,
    time_limit_seconds: float,
) -> chess.Move | None:
    limit = chess.engine.Limit(depth=depth, time=time_limit_seconds)
    result = engine.play(board, limit)
    return result.move


def _material_eval_cp(board: chess.Board) -> int:
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score


def _classify_delta(delta: int, white_to_move: bool) -> str:
    player_delta = delta if white_to_move else -delta
    loss = -player_delta

    if loss >= 200:
        return "blunder"
    if loss >= 50:
        return "mistake"
    if loss >= 20:
        return "inaccuracy"
    return "ok"
