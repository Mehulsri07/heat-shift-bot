"""Output guard: every number in the written text must come from the risk engine or the fixed copy.

Every hour and number below is a made-up TEST FIXTURE, not real forecast data.
"""

import re

import pytest

import guard
import risk

DEVANAGARI = re.compile(r"[ऀ-ॿ]")


def scored(*rows: tuple[str, float, float], direct_sun: bool = False) -> dict:
    hourly = [{"hour": hour, "temp_c": temp, "rh": rh} for hour, temp, rh in rows]
    return risk.score_hours(hourly, direct_sun, "07:00", "18:00")


@pytest.fixture
def score() -> dict:
    return scored(("11:00", 34, 50), ("12:00", 46, 20), ("13:00", 46, 20), ("14:00", 30, 40))


def test_numbers_the_engine_produced_pass(score: dict) -> None:
    text = "Stop outdoor work from 12:00 to 14:00. Highest heat index: 49.0°C at 13:00."
    assert guard.grounded([text], score)


def test_an_invented_temperature_fails(score: dict) -> None:
    assert not guard.grounded(["The heat will reach 47.5°C."], score)


def test_an_invented_time_fails(score: dict) -> None:
    assert not guard.grounded(["Stop at 15:30."], score)


def test_a_number_from_the_fixed_copy_is_allowed(score: dict) -> None:
    # "every 15 to 20 minutes" comes from the fixed copy, not from the model.
    assert guard.grounded(["Drink water every 15 to 20 minutes."], score)


def test_every_text_is_checked(score: dict) -> None:
    assert not guard.grounded(["Stop from 12:00.", "Also 47.5 degrees."], score)


def test_word_limits() -> None:
    assert guard.within_limits(" ".join(["word"] * 120), " ".join(["word"] * 60))
    assert not guard.within_limits(" ".join(["word"] * 121), "short")
    assert not guard.within_limits("short", " ".join(["word"] * 61))


def test_template_is_grounded_and_within_limits(score: dict) -> None:
    for language in ("hi", "en"):
        plan_text, voice_text = guard.template(score, language)
        assert guard.grounded([plan_text, voice_text], score)
        assert guard.within_limits(plan_text, voice_text)


def test_template_voice_is_always_hindi(score: dict) -> None:
    _, voice_text = guard.template(score, "en")
    assert DEVANAGARI.search(voice_text)


def test_template_states_the_stop_window_times(score: dict) -> None:
    plan_text, _ = guard.template(score, "en")
    assert "Stop outdoor work from 12:00 to 14:00." in plan_text


def test_template_without_a_stop_window_says_so() -> None:
    cool = scored(("09:00", 25, 40), ("10:00", 28, 40))
    plan_text, voice_text = guard.template(cool, "en")
    assert "No stop-work window today." in plan_text
    assert guard.grounded([plan_text, voice_text], cool)
