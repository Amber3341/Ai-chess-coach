import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    games: Mapped[list["Game"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Game(Base):
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    pgn_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    result: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    moves: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blunders: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mistakes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    inaccuracies: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    white_player: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    black_player: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    report_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    move_evaluations: Mapped[list["MoveEvaluation"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
    )
    user: Mapped["User"] = relationship(back_populates="games")


class MoveEvaluation(Base):
    __tablename__ = "move_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    game_id: Mapped[str] = mapped_column(
        ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ply: Mapped[int] = mapped_column(Integer, nullable=False)
    san: Mapped[str] = mapped_column(String(32), nullable=False)
    fen: Mapped[str] = mapped_column(Text, nullable=False)
    eval_cp: Mapped[int] = mapped_column(Integer, nullable=False)
    classification: Mapped[str] = mapped_column(String(20), nullable=False)
    best_move_uci: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    best_move_san: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    game: Mapped[Game] = relationship(back_populates="move_evaluations")
