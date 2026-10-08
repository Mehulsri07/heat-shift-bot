"""Routing and validation for handlers/api.py. No AWS: tables and planner are faked.

Every site, plan and number below is a made-up TEST FIXTURE, not real forecast data.
"""
import json
from datetime import timedelta

import pytest

from handlers import api

SITE_ID = "11111111-2222-3333-4444-555555555555"
FIXTURE_SITE = {
    "name": "FIXTURE site",
    "lat": 26.9,
    "lon": 75.8,
    "language": "hi",
    "shift_start": "07:00",
    "shift_end": "18:00",
    "direct_sun": True,
}
FIXTURE_RED_FLAG = "FIXTURE RED FLAG TEXT"


class FakeTable:
    def __init__(self, keys: tuple[str, ...]) -> None:
        self.keys = keys
        self.rows: dict[tuple, dict] = {}

    def put_item(self, Item: dict) -> None:
        self.rows[tuple(Item[k] for k in self.keys)] = dict(Item)

    def get_item(self, Key: dict) -> dict:
        row = self.rows.get(tuple(Key[k] for k in self.keys))
        return {"Item": dict(row)} if row else {}


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> dict:
    tables = {"SITES_TABLE": FakeTable(("site_id",)), "PLANS_TABLE": FakeTable(("site_id", "date"))}
    invoked: list[dict] = []
    monkeypatch.setattr(api, "_table", lambda env_name: tables[env_name])
    monkeypatch.setattr(api, "_invoke_planner", invoked.append)
    monkeypatch.setattr(api, "_audio_url", lambda key: f"https://fixture.invalid/{key}")
    monkeypatch.setattr(api, "_copy", lambda language: {"red_flag": FIXTURE_RED_FLAG})
    return {"sites": tables["SITES_TABLE"], "plans": tables["PLANS_TABLE"], "invoked": invoked}


def call(method: str, path: str, body: object = None) -> tuple[int, dict]:
    event = {"rawPath": path, "requestContext": {"http": {"method": method}}}
    if body is not None:
        event["body"] = body if isinstance(body, str) else json.dumps(body)
    response = api.handler(event, None)
    return response["statusCode"], json.loads(response["body"])


def today(offset: int = 0) -> str:
    return (api._now().date() + timedelta(days=offset)).isoformat()


def add_site(world: dict) -> None:
    world["sites"].put_item({**FIXTURE_SITE, "site_id": SITE_ID})


def add_plan(world: dict, day: str, **attrs: object) -> None:
    world["plans"].put_item({"site_id": SITE_ID, "date": day, "updated_at": api._now().isoformat(), **attrs})


def test_create_site_saves_it_and_returns_an_id(world: dict) -> None:
    status, body = call("POST", "/api/sites", FIXTURE_SITE)
    assert status == 201
    saved = world["sites"].rows[(body["site_id"],)]
    assert saved["name"] == "FIXTURE site" and saved["direct_sun"] is True
    assert world["invoked"] == []  # creating a site does not start a plan

    status, fetched = call("GET", f"/api/sites/{body['site_id']}")
    assert status == 200 and fetched["lat"] == 26.9 and fetched["shift_end"] == "18:00"


@pytest.mark.parametrize("field,value,code", [
    ("name", "", "invalid_name"),
    ("name", "x" * 61, "invalid_name"),
    ("lat", 91, "invalid_lat"),
    ("lat", True, "invalid_lat"),
    ("lon", "75.8", "invalid_lon"),
    ("language", "fr", "invalid_language"),
    ("shift_start", "7:00", "invalid_shift_start"),
    ("shift_end", "24:00", "invalid_shift_end"),
    ("shift_end", "06:00", "invalid_shift_end"),  # ends before it starts
    ("direct_sun", "yes", "invalid_direct_sun"),
])
def test_create_site_rejects_bad_fields(world: dict, field: str, value: object, code: str) -> None:
    assert call("POST", "/api/sites", {**FIXTURE_SITE, field: value}) == (400, {"error": code})
    assert world["sites"].rows == {}


@pytest.mark.parametrize("body", ["not json", "[1, 2]"])
def test_body_must_be_a_json_object(world: dict, body: str) -> None:
    assert call("POST", "/api/sites", body) == (400, {"error": "invalid_json"})


def test_unknown_site_and_unknown_route(world: dict) -> None:
    assert call("GET", f"/api/sites/{SITE_ID}") == (404, {"error": "site_not_found"})
    assert call("GET", "/api/sites/not-a-uuid") == (404, {"error": "not_found"})
    assert call("DELETE", f"/api/sites/{SITE_ID}") == (404, {"error": "not_found"})


def test_request_plan_marks_it_pending_and_starts_planner(world: dict) -> None:
    add_site(world)
    day = today(1)
    assert call("POST", f"/api/sites/{SITE_ID}/plans", {"date": day}) == (202, {"status": "pending"})
    assert world["invoked"] == [{"site_id": SITE_ID, "date": day, "mode": "plan"}]
    assert call("GET", f"/api/sites/{SITE_ID}/plans/{day}") == (
        200, {"status": "pending", "site_id": SITE_ID, "date": day})

    # Asking again while planner is still working does not start it twice.
    call("POST", f"/api/sites/{SITE_ID}/plans", {"date": day})
    assert len(world["invoked"]) == 1


def test_request_plan_reuses_a_ready_plan(world: dict) -> None:
    add_site(world)
    add_plan(world, today(), status="ready")
    assert call("POST", f"/api/sites/{SITE_ID}/plans", {"date": today()}) == (200, {"status": "ready"})
    assert world["invoked"] == []


@pytest.mark.parametrize("status,age_seconds", [("failed", 0), ("pending", 600)])
def test_request_plan_rebuilds_failed_and_stuck_plans(world: dict, status: str, age_seconds: int) -> None:
    add_site(world)
    stamp = (api._now() - timedelta(seconds=age_seconds)).isoformat()
    add_plan(world, today(), status=status)
    world["plans"].rows[(SITE_ID, today())]["updated_at"] = stamp
    assert call("POST", f"/api/sites/{SITE_ID}/plans", {"date": today()})[0] == 202
    assert len(world["invoked"]) == 1


def test_request_plan_validates_date_and_site(world: dict) -> None:
    assert call("POST", f"/api/sites/{SITE_ID}/plans", {"date": today()}) == (404, {"error": "site_not_found"})
    add_site(world)
    for bad in ("tomorrow", "2025-13-01", None, 20250520, today(4)):
        assert call("POST", f"/api/sites/{SITE_ID}/plans", {"date": bad}) == (400, {"error": "invalid_date"})
    # A past date is allowed: that is replay mode.
    assert call("POST", f"/api/sites/{SITE_ID}/plans", {"date": "2025-05-20"})[0] == 202


def test_get_plan_not_found(world: dict) -> None:
    assert call("GET", f"/api/sites/{SITE_ID}/plans/{today()}") == (404, {"error": "plan_not_found"})


def test_ready_plan_below_danger_has_no_red_flag(world: dict) -> None:
    add_site(world)
    hours = [{"hour": "07:00", "temp_c": 1, "rh": 2, "heat_index_c": 3, "band": "SAFE"}]
    add_plan(world, today(), status="ready", source="forecast", hours=hours, stop_window=None,
             max_band="SAFE", plan_text="FIXTURE PLAN TEXT", voice_text="FIXTURE VOICE TEXT")
    status, body = call("GET", f"/api/sites/{SITE_ID}/plans/{today()}")
    assert status == 200
    assert body["hours"] == hours and body["plan_text"] == "FIXTURE PLAN TEXT"
    assert body["red_flag"] is None and body["cooling_points"] == []
    assert body["audio_status"] == "none" and body["audio_url"] is None
    assert "voice_text" not in body and "updated_at" not in body


@pytest.mark.parametrize("band", ["DANGER", "EXTREME_DANGER"])
def test_danger_plan_carries_the_fixed_red_flag_text(world: dict, band: str) -> None:
    add_site(world)
    add_plan(world, today(), status="ready", max_band=band)
    assert call("GET", f"/api/sites/{SITE_ID}/plans/{today()}")[1]["red_flag"] == FIXTURE_RED_FLAG


def test_danger_plan_without_red_flag_text_is_an_error(world: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    add_site(world)
    add_plan(world, today(), status="ready", max_band="DANGER")
    monkeypatch.setattr(api, "_copy", lambda language: {})
    assert call("GET", f"/api/sites/{SITE_ID}/plans/{today()}") == (500, {"error": "server_error"})


def test_voice_flow(world: dict) -> None:
    add_site(world)
    voice = f"/api/sites/{SITE_ID}/plans/{today()}/voice"
    assert call("POST", voice) == (404, {"error": "plan_not_found"})

    add_plan(world, today(), status="pending")
    assert call("POST", voice) == (409, {"error": "plan_not_ready"})

    add_plan(world, today(), status="ready", max_band="SAFE", audio_status="none")
    assert call("POST", voice) == (202, {"audio_status": "pending"})
    assert world["invoked"] == [{"site_id": SITE_ID, "date": today(), "mode": "voice"}]
    call("POST", voice)
    assert len(world["invoked"]) == 1  # still in flight, not started twice

    add_plan(world, today(), status="ready", max_band="SAFE", audio_status="ready", audio_s3_key="voice/x.mp3")
    assert call("POST", voice) == (200, {"audio_status": "ready"})
    body = call("GET", f"/api/sites/{SITE_ID}/plans/{today()}")[1]
    assert body["audio_url"] == "https://fixture.invalid/voice/x.mp3"
