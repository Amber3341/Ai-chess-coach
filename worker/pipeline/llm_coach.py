import json
import logging
import time
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from api.config import get_settings
from worker.pipeline.stockfish_engine import MoveEvaluationResult
from worker.pipeline.report_builder import build_report
from worker.pipeline.rag_retriever import retrieve as rag_retrieve

logger = logging.getLogger(__name__)

GEMINI_MAX_ATTEMPTS = 3
GEMINI_RETRYABLE_MARKERS = (
    "503",
    "500",
    "UNAVAILABLE",
    "INTERNAL",
    "DEADLINE_EXCEEDED",
    "temporarily",
    "timeout",
)

class CoachNote(BaseModel):
    ply: int
    note: str

class LLMCoachingReport(BaseModel):
    summary: str
    opening_review: str
    middlegame_review: str
    endgame_review: str
    action_plan: list[str]
    coach_notes: list[CoachNote]

class GeminiCoach:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        if self.api_key:
            # Explicitly force http_options if we see connection resets, but 
            # google-genai uses requests by default!
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_report(
        self,
        white_player: str | None,
        black_player: str | None,
        result: str | None,
        evaluations: list[MoveEvaluationResult],
    ) -> dict:
        # 1. First generate the structural deterministic parts using the existing builder
        base_report = build_report(
            white_player=white_player,
            black_player=black_player,
            result=result,
            evaluations=evaluations,
        )

        if not self.client:
            return base_report

        # 2. Extract critical moments to pass to the LLM
        critical_moments = base_report["critical_moments"]
        if not critical_moments:
            return base_report  # No critical moments, fallback report is fine

        # 3. Build RAG context query from top critical moment
        top_moment = critical_moments[0]
        phase = "opening" if top_moment["move_number"] <= 15 else "middlegame" if top_moment["move_number"] <= 35 else "endgame"
        rag_query = f"{phase} chess: {top_moment['classification']} - played {top_moment['san']}, Stockfish preferred {top_moment.get('best_move_san') or top_moment.get('best_move_uci', '')}"
        theory_passages = rag_retrieve(rag_query, top_k=3)

        # 4. Create prompt with RAG context
        prompt = self._build_prompt(white_player, black_player, result, critical_moments, theory_passages)

        last_error: Exception | None = None
        for attempt in range(1, GEMINI_MAX_ATTEMPTS + 1):
            try:
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.4,
                    ),
                )
                
                # 5. Parse response and merge into base_report
                llm_data = json.loads(response.text)
                
                base_report["summary"] = llm_data.get("summary", base_report["summary"])
                base_report["opening_review"] = llm_data.get("opening_review", base_report["opening_review"])
                base_report["middlegame_review"] = llm_data.get("middlegame_review", base_report["middlegame_review"])
                base_report["endgame_review"] = llm_data.get("endgame_review", base_report["endgame_review"])
                base_report["action_plan"] = llm_data.get("action_plan", base_report["action_plan"])
                
                # Merge coach notes
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

            except Exception as e:
                last_error = e
                if attempt < GEMINI_MAX_ATTEMPTS and _is_retryable_gemini_error(e):
                    delay_seconds = 2 ** attempt
                    logger.warning(
                        "Gemini API attempt %s/%s failed with retryable error; retrying in %ss: %s",
                        attempt,
                        GEMINI_MAX_ATTEMPTS,
                        delay_seconds,
                        e,
                    )
                    time.sleep(delay_seconds)
                    continue

                logger.warning(
                    "Gemini LLM skipped after %s attempt(s); using deterministic fallback report: %s",
                    attempt,
                    e,
                )
                base_report["metadata"]["source_detail"] = f"Gemini LLM skipped after {attempt} attempt(s) (Error: {e})"
                return base_report

        base_report["metadata"]["source_detail"] = f"Gemini LLM skipped (Error: {last_error})"
        return base_report

    def _build_prompt(self, white, black, result, critical_moments, theory_passages: list[str] | None = None) -> str:
        cm_text = []
        for m in critical_moments:
            best_move = m['best_move_san'] or m['best_move_uci'] or 'unknown'
            cm_text.append(f"- Move {m['move_number']} ({m['side']}): {m['san']} (Classification: {m['classification']}). Engine eval went to {m['eval_cp']/100:+.2f}. Stockfish preferred {best_move}.")
        
        cm_str = "\n".join(cm_text)

        theory_block = ""
        if theory_passages:
            theory_items = "\n".join(f"- {p}" for p in theory_passages)
            theory_block = f"""

Relevant Chess Theory Context (use this to give theory-grounded advice):
{theory_items}
"""

        return f"""You are an expert chess coach. Analyze the following game summary and critical moments to provide a structured coaching report for the player.
        
Game: {white or 'White'} vs {black or 'Black'}
Result: {result or 'Unknown'}

Critical Moments identified by Stockfish:
{cm_str}
{theory_block}
Provide a JSON response strictly matching this schema:
{{
  "summary": "String, 2-3 sentence overview",
  "opening_review": "String, advice",
  "middlegame_review": "String, advice",
  "endgame_review": "String, advice",
  "action_plan": ["String", "String", "String"],
  "coach_notes": [
    {{
      "ply": 14,
      "note": "String, specific advice"
    }}
  ]
}}

Ensure the advice is encouraging, specific to the actual moves played, and actionable. Do not wrap the JSON in Markdown backticks (```). Return raw JSON only."""


def _is_retryable_gemini_error(exc: Exception) -> bool:
    message = str(exc)
    upper_message = message.upper()
    return any(marker in upper_message or marker in message for marker in GEMINI_RETRYABLE_MARKERS)
