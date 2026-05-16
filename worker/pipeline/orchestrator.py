from pathlib import Path

from sqlalchemy.orm import Session

from api.models import Game, MoveEvaluation
from worker.pipeline.report_builder import build_report
from worker.pipeline.stockfish_engine import evaluate_pgn_auto


class AnalysisError(RuntimeError):
    pass


def analyze_game(db: Session, game_id: str) -> Game:
    game = db.get(Game, game_id)
    if game is None:
        raise AnalysisError("Game not found.")

    game.status = "processing"
    game.error_message = None
    db.commit()

    try:
        pgn_text = Path(game.pgn_path).read_text(encoding="utf-8")
        evaluations = evaluate_pgn_auto(pgn_text)

        game.move_evaluations.clear()
        game.blunders = sum(1 for item in evaluations if item.classification == "blunder")
        game.mistakes = sum(1 for item in evaluations if item.classification == "mistake")
        game.inaccuracies = sum(
            1 for item in evaluations if item.classification == "inaccuracy"
        )
        game.report = build_report(
            white_player=game.white_player,
            black_player=game.black_player,
            result=game.result,
            evaluations=evaluations,
        )
        game.report_summary = game.report["summary"]
        game.status = "complete"

        for item in evaluations:
            game.move_evaluations.append(
                MoveEvaluation(
                    ply=item.ply,
                    san=item.san,
                    fen=item.fen,
                    eval_cp=item.eval_cp,
                    classification=item.classification,
                    best_move_uci=item.best_move_uci,
                    best_move_san=item.best_move_san,
                )
            )

        db.commit()
        db.refresh(game)
        return game
    except Exception as exc:
        game.status = "failed"
        game.error_message = str(exc) or repr(exc)
        db.commit()
        db.refresh(game)
        return game


def _build_summary(game: Game) -> str:
    white = game.white_player or "White"
    black = game.black_player or "Black"
    issue_count = game.blunders + game.mistakes + game.inaccuracies

    if issue_count == 0:
        return (
            f"{white} vs {black} was analyzed successfully. The local evaluator "
            "did not find any major loss moments in this first development pass."
        )

    return (
        f"{white} vs {black} was analyzed successfully. The evaluator found "
        f"{game.blunders} blunder(s), {game.mistakes} mistake(s), and "
        f"{game.inaccuracies} inaccuracy/inaccuracies."
    )
