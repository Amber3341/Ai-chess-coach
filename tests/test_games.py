from collections.abc import Generator
from pathlib import Path
import shutil
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.config import get_settings
from api.database import Base, get_db
from api.main import app
from worker.pipeline.stockfish_engine import evaluate_pgn_auto


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    test_dir = Path(".test_runtime") / str(uuid.uuid4())
    test_dir.mkdir(parents=True, exist_ok=True)
    test_engine = create_engine(
        f"sqlite:///{test_dir / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    testing_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(get_settings(), "upload_dir", test_dir / "uploads")
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()
        if test_dir.exists():
            shutil.rmtree(test_dir, ignore_errors=True)


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_valid_pgn(client: TestClient) -> None:
    pgn = """[Event "Casual Game"]
[White "Arjun"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0
"""

    response = client.post(
        "/api/v1/games",
        files={"file": ("game.pgn", pgn, "application/x-chess-pgn")},
    )

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"
    assert body["white_player"] == "Arjun"
    assert body["black_player"] == "Player2"
    assert body["result"] == "1-0"
    assert body["moves"] == 6


def test_list_games_returns_recent_uploads_first(client: TestClient) -> None:
    first_pgn = """[Event "First Game"]
[White "FirstWhite"]
[Black "FirstBlack"]
[Result "1-0"]

1. e4 e5 1-0
"""
    second_pgn = """[Event "Second Game"]
[White "SecondWhite"]
[Black "SecondBlack"]
[Result "0-1"]

1. d4 d5 0-1
"""

    first_response = client.post(
        "/api/v1/games",
        files={"file": ("first.pgn", first_pgn, "application/x-chess-pgn")},
    )
    second_response = client.post(
        "/api/v1/games",
        files={"file": ("second.pgn", second_pgn, "application/x-chess-pgn")},
    )

    response = client.get("/api/v1/games")

    assert response.status_code == 200
    games = response.json()
    assert [game["id"] for game in games] == [
        second_response.json()["id"],
        first_response.json()["id"],
    ]
    assert games[0]["white_player"] == "SecondWhite"


def test_run_local_analysis_completes_game_and_records_moves(client: TestClient) -> None:
    pgn = """[Event "Casual Game"]
[White "Arjun"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0
"""

    upload_response = client.post(
        "/api/v1/games",
        files={"file": ("game.pgn", pgn, "application/x-chess-pgn")},
    )
    game_id = upload_response.json()["id"]

    analysis_response = client.post(f"/api/v1/games/{game_id}/analyze")
    moves_response = client.get(f"/api/v1/games/{game_id}/moves")
    report_response = client.get(f"/api/v1/games/{game_id}/report")

    assert analysis_response.status_code == 200
    analyzed_game = analysis_response.json()
    assert analyzed_game["status"] == "complete"
    assert analyzed_game["report_summary"]

    assert moves_response.status_code == 200
    move_evaluations = moves_response.json()
    assert len(move_evaluations) == 6
    assert move_evaluations[0]["ply"] == 1
    assert move_evaluations[0]["san"] == "e4"
    assert move_evaluations[0]["classification"] == "ok"

    assert report_response.status_code == 200
    report = report_response.json()
    assert report["summary"]
    assert report["metadata"]["total_plies"] == 6
    assert set(report.keys()) == {
        "summary",
        "critical_moments",
        "opening_review",
        "middlegame_review",
        "endgame_review",
        "action_plan",
        "metadata",
    }


def test_report_not_ready_before_analysis(client: TestClient) -> None:
    pgn = """[Event "Casual Game"]
[White "Arjun"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 1-0
"""

    upload_response = client.post(
        "/api/v1/games",
        files={"file": ("game.pgn", pgn, "application/x-chess-pgn")},
    )
    game_id = upload_response.json()["id"]

    report_response = client.get(f"/api/v1/games/{game_id}/report")

    assert report_response.status_code == 409
    assert report_response.json()["detail"] == "Report is not ready yet."


def test_evaluate_pgn_auto_falls_back_without_stockfish() -> None:
    pgn = """[Event "Fallback Test"]
[White "Arjun"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 1-0
"""

    evaluations = evaluate_pgn_auto(pgn)

    assert len(evaluations) == 2
    assert evaluations[0].san == "e4"


def test_upload_pgn_with_blank_lines_between_headers(client: TestClient) -> None:
    pgn = """[Event "Sample ChessMentor Test Game"]

[Site "Local"]

[White "Arjun"]

[Black "Player2"]

[Result "1-0"]



1. e4 e5 2. Nf3 Nc6 1-0
"""

    response = client.post(
        "/api/v1/games",
        files={"file": ("game.pgn", pgn, "application/x-chess-pgn")},
    )

    assert response.status_code == 202
    assert response.json()["moves"] == 4
