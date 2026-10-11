"""Planner: building plans, voice notes and the daily run. AWS, Open-Meteo, Bedrock and Polly are all faked.

Every site, hour and text below is a made-up TEST FIXTURE, not real forecast data.
"""

from typing import Any

import pytest

import agent
import cooling
import forecast
import guard
import voice
from handlers import planner

SITE_ID = "11111111-2222-3333-4444-555555555555"
OTHER_SITE_ID = "66666666-7777-8888-9999-000000000000"
SITE = {
    "site_id": SITE_ID,
    "name": "FIXTURE site",
    "lat": 26.9,
    "lon": 75.8,
    "language": "en",
    "shift_start": "07:00",
    "shift_end": "18:00",
    "direct_sun": False,
}


class FakeTable:
    def __init__(self, keys: tuple[str, ...], rows: list[dict] | None = None) -> None:
        self.keys = keys
        self.rows: dict[tuple, dict] = {tuple(row[k] for k in keys): dict(row) for row in rows or []}

    def get_item(self, Key: dict) -> dict:
        row = self.rows.get(tuple(Key[k] for k in self.keys))
        return {"Item": dict(row)} if row else {}

    def update_item(self, Key: dict, UpdateExpression: str, ExpressionAttributeNames: dict,
                    ExpressionAttributeValues: dict) -> None:
        row = self.rows.setdefault(tuple(Key[k] for k in self.keys), dict(Key))
        for placeholder, name in ExpressionAttributeNames.items():
            row[name] = ExpressionAttributeValues[":" + placeholder[1:]]

    def scan(self, **_: Any) -> dict:
        return {"Items": [dict(row) for row in self.rows.values()]}


def fixture_hours() -> list[dict]:
    """A day with a DANGER run from 12:00 to 14:00, inside the shift."""
    hourly = []
    for hour in range(24):
        danger = 12 <= hour < 14
        hourly.append({
            "hour": f"{hour:02d}:00",
            "temp_c": 46.0 if danger else 30.0,
            "rh": 20.0 if danger else 40.0,
        })
    return hourly


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> dict:
    sites = FakeTable(("site_id",), [SITE])
    plans = FakeTable(("site_id", "date"))
    voiced: list[tuple[str, str]] = []
    monkeypatch.setattr(planner, "_table", lambda env: {"SITES_TABLE": sites, "PLANS_TABLE": plans}[env])
    monkeypatch.setattr(forecast, "get_hourly", lambda lat, lon, day: fixture_hours())
    monkeypatch.setattr(cooling, "nearest", lambda lat, lon, limit: [
        {"name": "FIXTURE water point", "type": "water", "lat": 26.91, "lon": 75.79, "distance_km": 0.4},
    ])
    monkeypatch.setattr(agent, "write_texts", lambda score, language: (
        "Stop outdoor work from 12:00 to 14:00.", "Aaj ki garmi ki yojana."))

    def make_voice(text: str, language: str) -> str:
        voiced.append((text, language))
        return "voice/fixture.mp3"

    monkeypatch.setattr(voice, "make_voice_note", make_voice)
    return {"sites": sites, "plans": plans, "voiced": voiced}


def today() -> str:
    return planner._now().date().isoformat()


def row(world: dict, day: str, site_id: str = SITE_ID) -> dict:
    return world["plans"].rows[(site_id, day)]


def test_plan_mode_saves_a_ready_plan(world: dict) -> None:
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "plan"}, None)
    saved = row(world, today())
    assert saved["status"] == "ready" and saved["source"] == "forecast"
    assert saved["stop_window"] == {"start": "12:00", "end": "14:00"}
    assert saved["max_band"] == "DANGER"
    assert saved["plan_text"] == "Stop outdoor work from 12:00 to 14:00."
    assert saved["voice_text"] == "Aaj ki garmi ki yojana."
    assert saved["cooling_points"][0]["name"] == "FIXTURE water point"
    assert saved["audio_status"] == "none"
    assert len(saved["hours"]) == 11  # the 07:00 to 17:59 shift, one row per hour


def test_a_past_date_is_a_replay(world: dict) -> None:
    planner.handler({"site_id": SITE_ID, "date": "2025-05-20", "mode": "plan"}, None)
    assert row(world, "2025-05-20")["source"] == "replay"


def test_an_ungrounded_agent_text_falls_back_to_the_template(world: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(agent, "write_texts", lambda score, language: ("It will hit 47.5 degrees.", "Garmi."))
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "plan"}, None)
    saved = row(world, today())
    assert saved["status"] == "ready"
    assert "47.5" not in saved["plan_text"]
    assert guard.grounded([saved["plan_text"], saved["voice_text"]], {
        "hours": saved["hours"], "stop_window": saved["stop_window"], "max_band": saved["max_band"]})


def test_an_agent_error_falls_back_to_the_template(world: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(score: dict, language: str) -> tuple[str, str]:
        raise RuntimeError("bedrock unavailable")

    monkeypatch.setattr(agent, "write_texts", broken)
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "plan"}, None)
    assert row(world, today())["status"] == "ready"


def test_a_cooling_error_does_not_block_the_plan(world: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(lat: float, lon: float, limit: int) -> list:
        raise cooling.CoolingError("table unreachable")

    monkeypatch.setattr(cooling, "nearest", broken)
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "plan"}, None)
    saved = row(world, today())
    assert saved["status"] == "ready" and saved["cooling_points"] == []


def test_a_forecast_failure_marks_the_plan_failed(world: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    def down(lat: float, lon: float, day: str) -> list:
        raise forecast.ForecastError("open-meteo timed out")

    monkeypatch.setattr(forecast, "get_hourly", down)
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "plan"}, None)
    saved = row(world, today())
    assert saved["status"] == "failed" and "updated_at" in saved


def test_voice_mode_makes_the_note_in_hindi(world: dict) -> None:
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "plan"}, None)
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "voice"}, None)
    assert world["voiced"] == [("Aaj ki garmi ki yojana.", "hi")]
    saved = row(world, today())
    assert saved["audio_status"] == "ready" and saved["audio_s3_key"] == "voice/fixture.mp3"


def test_voice_failure_marks_only_the_audio_failed(world: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "plan"}, None)

    def polly_down(text: str, language: str) -> str:
        raise RuntimeError("polly unavailable")

    monkeypatch.setattr(voice, "make_voice_note", polly_down)
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "voice"}, None)
    saved = row(world, today())
    assert saved["audio_status"] == "failed" and saved["status"] == "ready"


def test_voice_mode_needs_a_ready_plan(world: dict) -> None:
    planner.handler({"site_id": SITE_ID, "date": today(), "mode": "voice"}, None)
    assert world["voiced"] == []


def test_the_daily_run_isolates_one_failing_site(world: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    world["sites"].rows[(OTHER_SITE_ID,)] = {**SITE, "site_id": OTHER_SITE_ID}
    calls = {"n": 0}

    def fail_second(lat: float, lon: float, day: str) -> list:
        calls["n"] += 1
        if calls["n"] == 2:
            raise forecast.ForecastError("open-meteo timed out")
        return fixture_hours()

    monkeypatch.setattr(forecast, "get_hourly", fail_second)
    result = planner.handler({"all_sites": True}, None)
    assert result == {"built": 1, "failed": 1}
    statuses = {site: row(world, today(), site)["status"] for site in (SITE_ID, OTHER_SITE_ID)}
    assert sorted(statuses.values()) == ["failed", "ready"]
