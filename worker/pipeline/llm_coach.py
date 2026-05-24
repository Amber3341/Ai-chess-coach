"""
LLM coaching module.
Uses Gemini 2.5 Flash to generate a natural language coaching report
from the raw move evaluations and RAG context.

Optimizations applied:
  #1  - Query RAG for every critical moment (not just the top-1), deduplicated
  #2  - Richer, semantically dense RAG query strings
  #7  - Module-level GeminiCoach singleton (avoid repeated client instantiation)
  #8  - Phase error counts included in the prompt for grounded phase reviews
  #9  - Temperature lowered 0.4 -> 0.2 for more reliable JSON output
  #10 - Skill-level hint derived from blunder/mistake counts
  #11 - Native Gemini response_schema for strict JSON enforcement
  #14 - tenacity retry decorator instead of manual sleep loop
"""
import json
import logging
from google import genai
from google.genai import types

from api.config import get_settings
from worker.pipeline.stockfish_engine import MoveEvaluationResult
from worker.pipeline.report_builder import build_report
from worker.pipeline.rag_retriever import retrieve as rag_retrieve

logger = logging.getLogger(__name__)

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception,
        RetryError,
    )

    GEMINI_RETRYABLE_MARKERS = (
        "503",
        "500",
        "UNAVAILABLE",
        "INTERNAL",
        "DEADLINE_EXCEEDED",
        "temporarily",
        "timeout",
    )

    def _is_retryable(exc: BaseException) -> bool:
        msg = str(exc)
        upper = msg.upper()
        return any(m in upper or m in msg for m in GEMINI_RETRYABLE_MARKERS)

    _gemini_retry = retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8),
        retry=retry_if_exception(_is_retryable),
        reraise=True,
    )
    _HAS_TENACITY = True
    logger.debug("tenacity available - using decorator-based retry for Gemini calls.")

except ImportError:
    import time

    _HAS_TENACITY = False

    def _gemini_retry(fn):
        return fn

    logger.debug("tenacity not installed - Gemini retries disabled.")


_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "opening_review": {"type": "string"},
        "middlegame_review": {"type": "string"},
        "endgame_review": {"type": "string"},
        "action_plan": {
            "type": "array",
            "items": {"type": "string"},
        },
        "coach_notes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ply": {"type": "integer"},
                    "note": {"type": "string"},
                },
                "required": ["ply", "note"],
            },
        },
    },
    "required": [
        "summary",
        "opening_review",
        "middlegame_review",
        "endgame_review",
        "action_plan",
        "coach_notes",
    ],
}


def _phase_for_move(move_number: int) -> str:
    if move_number <= 15:
        return "opening"
    if move_number <= 35:
        return "middlegame"
    return "endgame"


_coach_singleton: "GeminiCoach | None" = None

def get_coach() -> "GeminiCoach":
    global _coach_singleton
    if _coach_singleton is None:
        _coach_singleton = GeminiCoach()
    return _coach_singleton


class GeminiCoach:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def generate_report(
        self,
        white_player: str | None,
        black_player: str | None,
        result: str | None,
        evaluations: list[MoveEvaluationResult],
    ) -> dict:
        base_report = build_report(
            white_player=white_player,
            black_player=black_player,
            result=result,
            evaluations=evaluations,
        )

        if not self.client:
            return base_report

        critical_moments = base_report["critical_moments"]
        if not critical_moments:
            return base_report

        theory_passages = self._gather_rag_passages(critical_moments)
        phase_counts = base_report.get("phase_counts", self._compute_phase_counts(evaluations))
        skill_hint = self._infer_skill_hint(base_report)

        prompt = self._build_prompt(
            white_player, black_player, result,
            critical_moments, theory_passages,
            phase_counts, skill_hint,
        )

        llm_data = self._call_gemini(prompt)
        if llm_data is None:
            return base_report

        base_report["summary"] = llm_data.get("summary", base_report["summary"])
        base_report["opening_review"] = llm_data.get("opening_review", base_report["opening_review"])
        base_report["middlegame_review"] = llm_data.get("middlegame_review", base_report["middlegame_review"])
        base_report["endgame_review"] = llm_data.get("endgame_review", base_report["endgame_review"])
        base_report["action_plan"] = llm_data.get("action_plan", base_report["action_plan"])

        notes_map = {item["ply"]: item["note"] for item in llm_data.get("coach_notes", [])}
        for moment in base_report["critical_moments"]:
            if moment["ply"] in notes_map:
                moment["coach_note"] = notes_map[moment["ply"]]

        base_report["metadata"]["source_detail"] = (
            "Coaching provided by Gemini 2.5 Flash + RAG"
            if theory_passages
            else "Coaching provided by Gemini 2.5 Flash"
        )

        return base_report

    def _gather_rag_passages(self, critical_moments: list[dict]) -> list[str]:
        seen: set[str] = set()
        passages: list[str] = []

        for moment in critical_moments:
            move_number = moment["move_number"]
            phase = _phase_for_move(move_number)
            classification = moment["classification"]
            san = moment["san"]
            best_move = moment.get("best_move_san") or moment.get("best_move_uci") or "unknown"
            eval_pawns = moment["eval_cp"] / 100

            query = (
                f"{phase} chess {classification}: player played {san} "
                f"(eval {eval_pawns:+.1f} pawns, engine prefers {best_move}). "
                f"How to avoid {classification}s in the {phase} and what principle applies."
            )

            for passage in rag_retrieve(query, top_k=3, phase=phase):
                if passage not in seen:
                    seen.add(passage)
                    passages.append(passage)
                    if len(passages) >= 10:
                        return passages

        return passages

    def _compute_phase_counts(self, evaluations: list[MoveEvaluationResult]) -> dict:
        counts: dict[str, dict[str, int]] = {
            "opening": {"blunder": 0, "mistake": 0, "inaccuracy": 0},
            "middlegame": {"blunder": 0, "mistake": 0, "inaccuracy": 0},
            "endgame": {"blunder": 0, "mistake": 0, "inaccuracy": 0},
        }
        for ev in evaluations:
            if ev.classification in ("blunder", "mistake", "inaccuracy"):
                phase = _phase_for_move((ev.ply + 1) // 2)
                counts[phase][ev.classification] += 1
        return counts

    def _infer_skill_hint(self, base_report: dict) -> str:
        meta = base_report.get("metadata", {})
        blunders = meta.get("blunders", 0)
        mistakes = meta.get("mistakes", 0)

        if blunders >= 3:
            return (
                "The player appears to be a beginner or lower-intermediate "
                "(800-1100 ELO). Give simple, encouraging, concrete advice."
            )
        if blunders >= 1 or mistakes >= 3:
            return (
                "The player appears to be an intermediate club player "
                "(1100-1400 ELO). Balance tactical and positional feedback."
            )
        return (
            "The player appears to be an advanced club player "
            "(1400-1800 ELO). Include nuanced positional and strategic insights."
        )

    def _build_prompt(
        self,
        white: str | None,
        black: str | None,
        result: str | None,
        critical_moments: list[dict],
        theory_passages: list[str] | None,
        phase_counts: dict,
        skill_hint: str,
    ) -> str:
        cm_lines = []
        for m in critical_moments:
            best_move = m.get("best_move_san") or m.get("best_move_uci") or "unknown"
            best_line = m.get("best_line_san")
            line_text = f" Best line: {' '.join(best_line[:3])}." if best_line else ""
            cm_lines.append(
                f"- Move {m['move_number']} ({m['side']}): {m['san']} "
                f"[{m['classification']}] - eval {m['eval_cp']/100:+.2f} pawns. "
                f"Engine preferred {best_move}.{line_text}"
            )
        cm_str = "\n".join(cm_lines)

        phase_summary = (
            f"Phase Error Summary:\n"
            f"  Opening  (moves 1-15):  "
            f"{phase_counts['opening']['blunder']} blunder(s), "
            f"{phase_counts['opening']['mistake']} mistake(s), "
            f"{phase_counts['opening']['inaccuracy']} inaccuracy/inaccuracies\n"
            f"  Middlegame (moves 16-35): "
            f"{phase_counts['middlegame']['blunder']} blunder(s), "
            f"{phase_counts['middlegame']['mistake']} mistake(s), "
            f"{phase_counts['middlegame']['inaccuracy']} inaccuracy/inaccuracies\n"
            f"  Endgame  (moves 36+):  "
            f"{phase_counts['endgame']['blunder']} blunder(s), "
            f"{phase_counts['endgame']['mistake']} mistake(s), "
            f"{phase_counts['endgame']['inaccuracy']} inaccuracy/inaccuracies"
        )

        theory_block = ""
        if theory_passages:
            theory_items = "\n".join(f"- {p}" for p in theory_passages)
            theory_block = (
                f"\nRelevant Chess Theory (use this to ground your advice in established principles):\n"
                f"{theory_items}\n"
            )

        return (
            f"You are an expert chess coach. Analyze this game and produce a structured coaching report.\n\n"
            f"Game: {white or 'White'} vs {black or 'Black'}\n"
            f"Result: {result or 'Unknown'}\n\n"
            f"Skill Assessment: {skill_hint}\n\n"
            f"{phase_summary}\n\n"
            f"Critical Moments identified by Stockfish:\n{cm_str}\n"
            f"{theory_block}\n"
            f"Instructions:\n"
            f"- Write a 2-3 sentence summary of the game.\n"
            f"- Write opening_review, middlegame_review, and endgame_review using the phase error data above.\n"
            f"- Provide 3 specific, actionable items in action_plan.\n"
            f"- For each critical moment listed, write a coach_note entry (ply number matches the move).\n"
            f"- Advice must be encouraging, specific to actual moves played, and appropriate for the player's skill level.\n"
            f"- Ground phase reviews in the chess theory passages provided where applicable.\n"
        )

    def _call_gemini(self, prompt: str) -> dict | None:
        assert self.client is not None

        if _HAS_TENACITY:
            @_gemini_retry
            def _do_call():
                return self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=_RESPONSE_SCHEMA,
                        temperature=0.2,
                    ),
                )
        else:
            def _do_call():
                return self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=_RESPONSE_SCHEMA,
                        temperature=0.2,
                    ),
                )

        try:
            response = _do_call()
            return json.loads(response.text)
        except Exception as e:
            logger.warning(
                "Gemini LLM call failed; using deterministic fallback report. Error: %s", e
            )
            return None
