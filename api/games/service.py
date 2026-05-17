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


async def create_game_from_upload(db: Session, upload: UploadFile, user_id: str) -> Game:
    if not upload.filename or not upload.filename.lower().endswith(".pgn"):
        raise InvalidPGNError("Only .pgn files are supported.")

    raw = await upload.read()
    try:
        pgn_text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidPGNError("PGN must be a UTF-8 text file.") from exc

    pgn_text = normalize_pgn_text(pgn_text)
    metadata = parse_pgn(pgn_text)
    from api.storage import save_pgn
    
    game = Game(
        pgn_path="",
        status="pending",
        result=metadata["result"],
        moves=metadata["moves"],
        white_player=metadata["white_player"],
        black_player=metadata["black_player"],
        user_id=user_id,
    )
    db.add(game)
    db.flush()

    # Save to GCS or fallback to local
    pgn_uri = save_pgn(str(game.id), pgn_text)
    game.pgn_path = pgn_uri

    db.commit()
    db.refresh(game)
    return game


def get_game(db: Session, game_id: str, user_id: str) -> Game | None:
    return db.query(Game).filter(Game.id == game_id, Game.user_id == user_id).first()


def list_games(db: Session, user_id: str, limit: int = 20) -> list[Game]:
    return (
        db.query(Game)
        .filter(Game.user_id == user_id)
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
