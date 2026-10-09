"""Output guard and template fallback.

The model writes the plan text, but every number in it must come from the risk engine or from the fixed
copy. A text that breaks that rule is thrown away and the template text is used instead.
"""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path
from typing import Any

COPY_DIR = Path(__file__).parent / "copy"
NUMBER = re.compile(r"\d+(?::\d{2}|\.\d+)?")  # 14:00, 33.1, 12
PLAN_WORD_LIMIT = 120
VOICE_WORD_LIMIT = 60


@cache
def load_copy(language: str) -> dict[str, str]:
    return json.loads((COPY_DIR / f"{language}.json").read_text(encoding="utf-8"))


def _numbers(text: str) -> set[str]:
    return set(NUMBER.findall(text))


def _rendered(value: float) -> set[str]:
    return {f"{value:.1f}", f"{value:.0f}"}


def _engine_numbers(score: dict[str, Any]) -> set[str]:
    allowed: set[str] = set()
    for item in score["hours"]:
        allowed.add(item["hour"])
        for value in (item["temp_c"], item["rh"], item["heat_index_c"]):
            allowed |= _rendered(value)
    window = score["stop_window"]
    if window:
        allowed |= {window["start"], window["end"]}
    return allowed


def _copy_numbers() -> set[str]:
    allowed: set[str] = set()
    for language in ("hi", "en"):
        for text in load_copy(language).values():
            allowed |= _numbers(text)
    return allowed


def grounded(texts: list[str], score: dict[str, Any]) -> bool:
    """True when every number in `texts` is one the engine produced or the fixed copy contains."""
    allowed = _engine_numbers(score) | _copy_numbers()
    return all(_numbers(text) <= allowed for text in texts)


def within_limits(plan_text: str, voice_text: str) -> bool:
    return len(plan_text.split()) <= PLAN_WORD_LIMIT and len(voice_text.split()) <= VOICE_WORD_LIMIT


def template(score: dict[str, Any], language: str) -> tuple[str, str]:
    """Build the plan and the Hindi voice script from copy and engine output only.

    The plan is in the site's language; the voice script is always Hindi.
    """
    site = load_copy(language)
    hindi = load_copy("hi")
    peak = max(score["hours"], key=lambda item: item["heat_index_c"])
    top_band = score["max_band"]
    window = score["stop_window"]

    stop = site["stop_yes"].format(**window) if window else site["stop_no"]
    plan_text = " ".join([
        stop,
        site["peak_line"].format(hi=f"{peak['heat_index_c']:.1f}", hour=peak["hour"]),
        site["max_line"].format(band=site[f"band_{top_band}"]),
        site[f"action_{top_band}"],
    ])

    voice_stop = hindi["stop_yes"].format(**window) if window else hindi["stop_no"]
    voice_text = " ".join([hindi["voice_intro"], voice_stop, hindi[f"action_{top_band}"]])
    return plan_text, voice_text
