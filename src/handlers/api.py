"""JSON API for the app: sites, plans and voice notes. Plan building is handed to planner."""
import base64
import json
import logging
import os
import re
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable

import boto3

log = logging.getLogger()
log.setLevel(logging.INFO)

# India has no daylight saving, so a fixed offset is exact and needs no tz database.
IST = timezone(timedelta(hours=5, minutes=30), "Asia/Kolkata")
HHMM = re.compile(r"([01]\d|2[0-3]):[0-5]\d")
SITE = r"(?P<site_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"
DATE = r"(?P<day>\d{4}-\d{2}-\d{2})"
RED_FLAG_BANDS = {"DANGER", "EXTREME_DANGER"}
MAX_DAYS_AHEAD = 3
# planner times out at 120 s; a row still pending after this is treated as dead and rebuilt.
STALE_AFTER = timedelta(seconds=150)
AUDIO_LINK_SECONDS = 3600
PLAN_FIELDS = ("source", "hours", "stop_window", "max_band", "plan_text")


class ApiError(Exception):
    def __init__(self, status: int, code: str) -> None:
        super().__init__(code)
        self.status = status
        self.code = code


def _table(env_name: str) -> Any:
    return boto3.resource("dynamodb").Table(os.environ[env_name])


def _invoke_planner(payload: dict) -> None:
    boto3.client("lambda").invoke(
        FunctionName=os.environ["PLANNER_FUNCTION_NAME"],
        InvocationType="Event",
        Payload=json.dumps(payload),
    )


def _audio_url(key: str) -> str:
    return boto3.client("s3").generate_presigned_url(
        "get_object",
        Params={"Bucket": os.environ["AUDIO_BUCKET"], "Key": key},
        ExpiresIn=AUDIO_LINK_SECONDS,
    )


def _copy(language: str) -> dict:
    path = Path(__file__).parent.parent / "copy" / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _now() -> datetime:
    return datetime.now(IST)


def _json(status: int, payload: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(payload, default=_plain, ensure_ascii=False),
    }


def _plain(value: Any) -> Any:
    if isinstance(value, Decimal):
        return int(value) if value == value.to_integral_value() else float(value)
    raise TypeError(type(value).__name__)


def _body(event: dict) -> dict:
    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8")
    try:
        body = json.loads(raw)
    except ValueError:
        raise ApiError(400, "invalid_json")
    if not isinstance(body, dict):
        raise ApiError(400, "invalid_json")
    return body


def _number(body: dict, field: str, low: float, high: float) -> Decimal:
    value = body.get(field)
    # bool is an int in Python; a true/false latitude is not a number.
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
        raise ApiError(400, f"invalid_{field}")
    return Decimal(str(value))


def _valid_site(body: dict) -> dict:
    name = body.get("name")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 60:
        raise ApiError(400, "invalid_name")
    lat = _number(body, "lat", -90, 90)
    lon = _number(body, "lon", -180, 180)
    if body.get("language") not in ("hi", "en"):
        raise ApiError(400, "invalid_language")
    for field in ("shift_start", "shift_end"):
        if not isinstance(body.get(field), str) or not HHMM.fullmatch(body[field]):
            raise ApiError(400, f"invalid_{field}")
    if body["shift_start"] >= body["shift_end"]:
        raise ApiError(400, "invalid_shift_end")
    if not isinstance(body.get("direct_sun"), bool):
        raise ApiError(400, "invalid_direct_sun")
    return {
        "name": name.strip(),
        "lat": lat,
        "lon": lon,
        "language": body["language"],
        "shift_start": body["shift_start"],
        "shift_end": body["shift_end"],
        "direct_sun": body["direct_sun"],
    }


def _site(site_id: str) -> dict:
    site = _table("SITES_TABLE").get_item(Key={"site_id": site_id}).get("Item")
    if not site:
        raise ApiError(404, "site_not_found")
    return site


def _plan(site_id: str, day: str) -> dict | None:
    return _table("PLANS_TABLE").get_item(Key={"site_id": site_id, "date": day}).get("Item")


def _in_flight(plan: dict) -> bool:
    """True while planner can still be working on this row."""
    try:
        return _now() - datetime.fromisoformat(plan["updated_at"]) < STALE_AFTER
    except (KeyError, ValueError):
        return False


def create_site(body: dict) -> dict:
    site = _valid_site(body)
    site["site_id"] = str(uuid.uuid4())
    site["created_at"] = _now().isoformat()
    _table("SITES_TABLE").put_item(Item=site)
    return _json(201, {"site_id": site["site_id"]})


def get_site(body: dict, site_id: str) -> dict:
    return _json(200, _site(site_id))


def request_plan(body: dict, site_id: str) -> dict:
    try:
        day = date.fromisoformat(body.get("date", ""))
    except (TypeError, ValueError):
        raise ApiError(400, "invalid_date")
    if day > _now().date() + timedelta(days=MAX_DAYS_AHEAD):
        raise ApiError(400, "invalid_date")
    _site(site_id)
    plan = _plan(site_id, day.isoformat())
    if plan and plan.get("status") == "ready":
        return _json(200, {"status": "ready"})
    if not (plan and plan.get("status") == "pending" and _in_flight(plan)):
        # ponytail: two requests in the same instant can both start planner; the route is
        # throttled and the second write wins. Use a conditional put if that ever matters.
        _table("PLANS_TABLE").put_item(Item={
            "site_id": site_id,
            "date": day.isoformat(),
            "status": "pending",
            "audio_status": "none",
            "updated_at": _now().isoformat(),
        })
        _invoke_planner({"site_id": site_id, "date": day.isoformat(), "mode": "plan"})
    return _json(202, {"status": "pending"})


def get_plan(body: dict, site_id: str, day: str) -> dict:
    plan = _plan(site_id, day)
    if not plan:
        raise ApiError(404, "plan_not_found")
    out = {"status": plan.get("status"), "site_id": site_id, "date": day}
    if out["status"] != "ready":
        return _json(200, out)
    out.update({field: plan.get(field) for field in PLAN_FIELDS})
    out["cooling_points"] = plan.get("cooling_points", [])
    # The red-flag text is fixed and human-reviewed. It is attached here, from the copy
    # file, so it never passes through the model. A missing text is an error, not a blank.
    out["red_flag"] = None
    if plan.get("max_band") in RED_FLAG_BANDS:
        out["red_flag"] = _copy(_site(site_id)["language"])["red_flag"]
    out["audio_status"] = plan.get("audio_status", "none")
    ready = out["audio_status"] == "ready" and plan.get("audio_s3_key")
    out["audio_url"] = _audio_url(plan["audio_s3_key"]) if ready else None
    return _json(200, out)


def request_voice(body: dict, site_id: str, day: str) -> dict:
    plan = _plan(site_id, day)
    if not plan:
        raise ApiError(404, "plan_not_found")
    if plan.get("status") != "ready":
        raise ApiError(409, "plan_not_ready")
    if plan.get("audio_status") == "ready":
        return _json(200, {"audio_status": "ready"})
    if not (plan.get("audio_status") == "pending" and _in_flight(plan)):
        plan["audio_status"] = "pending"
        plan["updated_at"] = _now().isoformat()
        _table("PLANS_TABLE").put_item(Item=plan)
        _invoke_planner({"site_id": site_id, "date": day, "mode": "voice"})
    return _json(202, {"audio_status": "pending"})


ROUTES: list[tuple[str, re.Pattern, Callable[..., dict]]] = [
    ("POST", re.compile(r"/api/sites"), create_site),
    ("GET", re.compile(rf"/api/sites/{SITE}"), get_site),
    ("POST", re.compile(rf"/api/sites/{SITE}/plans"), request_plan),
    ("GET", re.compile(rf"/api/sites/{SITE}/plans/{DATE}"), get_plan),
    ("POST", re.compile(rf"/api/sites/{SITE}/plans/{DATE}/voice"), request_voice),
]


def handler(event: dict, context: object) -> dict:
    path = event.get("rawPath", "")
    try:
        method = event["requestContext"]["http"]["method"]
        for route_method, pattern, view in ROUTES:
            match = pattern.fullmatch(path)
            if match and method == route_method:
                return view(_body(event), **match.groupdict())
        raise ApiError(404, "not_found")
    except ApiError as err:
        return _json(err.status, {"error": err.code})
    except Exception:
        # The path carries the site_id; the traceback goes to CloudWatch, never to the app.
        log.exception("api error on %s", path)
        return _json(500, {"error": "server_error"})
