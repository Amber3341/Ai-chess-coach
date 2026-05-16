from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GameResponse(BaseModel):
    id: str
    status: str
    result: str | None = None
    moves: int | None = None
    blunders: int = 0
    mistakes: int = 0
    inaccuracies: int = 0
    white_player: str | None = None
    black_player: str | None = None
    report_summary: str | None = None
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MoveEvaluationResponse(BaseModel):
    ply: int
    san: str
    fen: str
    eval_cp: int
    classification: str
    best_move_uci: str | None = None
    best_move_san: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CriticalMomentResponse(BaseModel):
    ply: int
    move_number: int
    side: str
    san: str
    fen: str
    eval_cp: int
    classification: str
    best_move_uci: str | None = None
    best_move_san: str | None = None
    coach_note: str


class ReportMetadataResponse(BaseModel):
    white_player: str
    black_player: str
    result: str | None = None
    total_plies: int
    blunders: int
    mistakes: int
    inaccuracies: int
    source: str
    source_detail: str | None = None


class GameReportResponse(BaseModel):
    summary: str
    critical_moments: list[CriticalMomentResponse]
    opening_review: str
    middlegame_review: str
    endgame_review: str
    action_plan: list[str] = Field(default_factory=list)
    metadata: ReportMetadataResponse
