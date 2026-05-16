from worker.pipeline.stockfish_engine import MoveEvaluationResult


CRITICAL_CLASSIFICATIONS = {"blunder", "mistake", "inaccuracy"}


def build_report(
    *,
    white_player: str | None,
    black_player: str | None,
    result: str | None,
    evaluations: list[MoveEvaluationResult],
) -> dict:
    white = white_player or "White"
    black = black_player or "Black"
    critical_moments = _critical_moments(evaluations)
    phase_counts = _phase_counts(evaluations)

    return {
        "summary": _summary_text(white, black, result, critical_moments),
        "critical_moments": critical_moments,
        "opening_review": _phase_review("opening", phase_counts["opening"]),
        "middlegame_review": _phase_review("middlegame", phase_counts["middlegame"]),
        "endgame_review": _phase_review("endgame", phase_counts["endgame"]),
        "action_plan": _action_plan(critical_moments),
        "metadata": {
            "white_player": white,
            "black_player": black,
            "result": result,
            "total_plies": len(evaluations),
            "blunders": _count(evaluations, "blunder"),
            "mistakes": _count(evaluations, "mistake"),
            "inaccuracies": _count(evaluations, "inaccuracy"),
            "source": evaluations[0].source if evaluations else "none",
            "source_detail": evaluations[0].source_detail if evaluations else None,
        },
    }


def _summary_text(
    white: str,
    black: str,
    result: str | None,
    critical_moments: list[dict],
) -> str:
    if not critical_moments:
        return (
            f"{white} vs {black} ({result or 'unknown result'}) was analyzed. "
            "The engine did not flag major evaluation-loss moments."
        )

    return (
        f"{white} vs {black} ({result or 'unknown result'}) was analyzed. "
        f"The engine flagged {len(critical_moments)} key moment(s), led by "
        f"move {critical_moments[0]['move_number']} {critical_moments[0]['san']}."
    )


def _critical_moments(evaluations: list[MoveEvaluationResult]) -> list[dict]:
    severity = {"blunder": 3, "mistake": 2, "inaccuracy": 1, "ok": 0}
    candidates = [
        item
        for item in evaluations
        if item.classification in CRITICAL_CLASSIFICATIONS
    ]
    candidates.sort(
        key=lambda item: (severity[item.classification], abs(item.eval_cp)),
        reverse=True,
    )

    return [
        {
            "ply": item.ply,
            "move_number": (item.ply + 1) // 2,
            "side": "white" if item.ply % 2 == 1 else "black",
            "san": item.san,
            "fen": item.fen,
            "eval_cp": item.eval_cp,
            "classification": item.classification,
            "best_move_uci": item.best_move_uci,
            "best_move_san": item.best_move_san,
            "coach_note": _coach_note(item),
        }
        for item in candidates[:3]
    ]


def _coach_note(item: MoveEvaluationResult) -> str:
    eval_pawns = item.eval_cp / 100
    best_move = item.best_move_san or item.best_move_uci
    best_move_text = (
        f" Stockfish preferred {best_move} instead." if best_move else ""
    )
    return (
        f"Engine evaluation after {item.san} is {eval_pawns:+.2f}. "
        f"Treat this as a {item.classification} candidate and review the tactic "
        "or positional concession around this move."
        f"{best_move_text}"
    )


def _phase_counts(evaluations: list[MoveEvaluationResult]) -> dict[str, dict[str, int]]:
    phases = {
        "opening": {"blunder": 0, "mistake": 0, "inaccuracy": 0},
        "middlegame": {"blunder": 0, "mistake": 0, "inaccuracy": 0},
        "endgame": {"blunder": 0, "mistake": 0, "inaccuracy": 0},
    }

    for item in evaluations:
        if item.classification not in CRITICAL_CLASSIFICATIONS:
            continue
        phases[_phase_for_ply(item.ply)][item.classification] += 1

    return phases


def _phase_for_ply(ply: int) -> str:
    move_number = (ply + 1) // 2
    if move_number <= 15:
        return "opening"
    if move_number <= 35:
        return "middlegame"
    return "endgame"


def _phase_review(phase: str, counts: dict[str, int]) -> str:
    total = sum(counts.values())
    if total == 0:
        return f"The {phase} did not contain major engine-flagged issues."

    return (
        f"The {phase} contained {counts['blunder']} blunder(s), "
        f"{counts['mistake']} mistake(s), and {counts['inaccuracy']} "
        "inaccuracy/inaccuracies."
    )


def _action_plan(critical_moments: list[dict]) -> list[str]:
    if not critical_moments:
        return [
            "Replay the full game and note where your plan changed.",
            "Compare your opening setup with a trusted model game.",
            "Practice converting small advantages without forcing tactics.",
        ]

    return [
        _action_item(moment)
        for moment in critical_moments
    ]


def _count(evaluations: list[MoveEvaluationResult], classification: str) -> int:
    return sum(1 for item in evaluations if item.classification == classification)


def _action_item(moment: dict) -> str:
    best_move = moment.get("best_move_san") or moment.get("best_move_uci")
    if best_move:
        return (
            f"Review move {moment['move_number']} {moment['san']} and compare it "
            f"against Stockfish's recommendation {best_move}."
        )

    return (
        f"Review move {moment['move_number']} {moment['san']} and find two safer alternatives."
    )
