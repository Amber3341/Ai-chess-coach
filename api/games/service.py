import io
from pathlib import Path

import chess.pgn
from fastapi import UploadFile
from sqlalchemy.orm import Session

from api.config import get_settings
from api.games.pgn import normalize_pgn_text
from api.models import Game, MoveEvaluation


class InvalidPGNError(ValueError):
    pass


def parse_pgn(pgn_text: str) -> dict[str, str | int | None]:
    game = chess.pgn.read_game(io.StringIO(normalize_pgn_text(pgn_text)))
    if game is None:
        raise InvalidPGNError("Uploaded file does not contain a valid PGN game.")

    moves = list(game.mainline_moves())
    if not moves:
        raise InvalidPGNError("PGN contains no playable moves.")

    if len(moves) > 150:
        raise InvalidPGNError("PGN exceeds the MVP limit of 150 moves.")

    headers = game.headers
    return {
        "result": headers.get("Result"),
        "moves": len(moves),
        "white_player": headers.get("White"),
        "black_player": headers.get("Black"),
    }


async def create_game_from_upload(db: Session, upload: UploadFile) -> Game:
    if not upload.filename or not upload.filename.lower().endswith(".pgn"):
        raise InvalidPGNError("Only .pgn files are supported.")

    raw = await upload.read()
    try:
        pgn_text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidPGNError("PGN must be a UTF-8 text file.") from exc

    pgn_text = normalize_pgn_text(pgn_text)
    metadata = parse_pgn(pgn_text)
    settings = get_settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    game = Game(
        pgn_path="",
        status="pending",
        result=metadata["result"],
        moves=metadata["moves"],
        white_player=metadata["white_player"],
        black_player=metadata["black_player"],
    )
    db.add(game)
    db.flush()

    pgn_path = Path(settings.upload_dir) / f"{game.id}.pgn"
    pgn_path.write_text(pgn_text, encoding="utf-8")
    game.pgn_path = str(pgn_path)

    db.commit()
    db.refresh(game)
    return game


def get_game(db: Session, game_id: str) -> Game | None:
    return db.get(Game, game_id)


def list_games(db: Session, limit: int = 20) -> list[Game]:
    return (
        db.query(Game)
        .order_by(Game.created_at.desc())
        .limit(limit)
        .all()
    )


def list_move_evaluations(db: Session, game_id: str) -> list[MoveEvaluation]:
    return (
        db.query(MoveEvaluation)
        .filter(MoveEvaluation.game_id == game_id)
        .order_by(MoveEvaluation.ply)
        .all()
    )
