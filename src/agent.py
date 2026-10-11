"""Strands agent that words the plan from the risk engine's output.

The agent never decides a band, a temperature or a time. It receives the scored hours and writes two short
texts from them. planner.py checks every number it writes and falls back to the template when it breaks the rules.
"""

from __future__ import annotations

import json
import os
from typing import Any

from strands import Agent
from strands.models import BedrockModel

SYSTEM_PROMPT = """You write a heat-safety shift plan for a construction-site supervisor in India.

You receive JSON with the risk engine's output: scored hours, the stop-work window and the highest band.
The engine has already decided everything. Your job is only to explain it in plain words.

Rules:
1. Use only the numbers and times that appear in the input. Never invent, round or estimate a number or time.
2. Never state a band that is not in the input. Never recommend a band or a temperature of your own.
3. Return a JSON object with exactly two keys:
   "plan_text": the supervisor's plan, at most 120 words, in the language given in "language".
   "voice_text": a short script for the crew voice note, at most 60 words, ALWAYS in Hindi,
                 simple and conversational, not formal.
4. Do not write any safety warning about heat stroke or first aid. The app adds a fixed warning itself.
5. Return only the JSON object, with no other text."""


def _model() -> BedrockModel:
    return BedrockModel(model_id=os.environ["BEDROCK_MODEL_ID"], temperature=0.2)


def _json_object(text: str) -> dict[str, Any]:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("the agent did not return a JSON object")
    data = json.loads(text[start : end + 1])
    if not isinstance(data, dict) or not isinstance(data.get("plan_text"), str) or not isinstance(data.get("voice_text"), str):
        raise ValueError("the agent's JSON is missing plan_text or voice_text")
    return data


def write_texts(score: dict[str, Any], language: str) -> tuple[str, str]:
    """Return (plan_text, voice_text) written from the engine's output. Raises on any failure."""
    agent = Agent(model=_model(), system_prompt=SYSTEM_PROMPT, callback_handler=None)
    payload = {"language": language, **score}
    result = agent(json.dumps(payload, ensure_ascii=False))
    data = _json_object(str(result))
    return data["plan_text"].strip(), data["voice_text"].strip()
