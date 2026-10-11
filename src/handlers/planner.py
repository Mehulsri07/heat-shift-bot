"""Planner: builds a site's plan, makes its crew voice note, and runs the 06:00 job for every site.

It is invoked asynchronously by the api Lambda (or by the daily schedule). It is never retried: a failure marks the
row as failed, so a crash cannot build or voice the same plan twice.
"""

from __future__ import annotations

import logging
import os
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import boto3

import agent
import cooling
import forecast
import guard
import risk
import voice

log = logging.getLogger()
log.setLevel(logging.INFO)

IST = timezone(timedelta(hours=5, minutes=30), "Asia/Kolkata")
# The crew note is always in Hindi, whatever the app language.
VOICE_LANGUAGE = "hi"
COOLING_LIMIT = 3


def _now() -> datetime:
    return datetime.now(IST)


def _dec(value: Any) -> Any:
    """DynamoDB stores numbers as Decimal, never float."""
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: _dec(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_dec(item) for item in value]
    return value


def _table(env_name: str) -> Any:
    return boto3.resource("dynamodb").Table(os.environ[env_name])


def _set(site_id: str, day: str, **attrs: Any) -> None:
    """Write some attributes on a plan row and refresh updated_at, which api uses to spot stuck plans."""
    attrs["updated_at"] = _now().isoformat()
    names = {f"#{key}": key for key in attrs}
    values = {f":{key}": _dec(value) for key, value in attrs.items()}
    _table("PLANS_TABLE").update_item(
        Key={"site_id": site_id, "date": day},
        UpdateExpression="SET " + ", ".join(f"#{key} = :{key}" for key in attrs),
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
    )


def _site(site_id: str) -> dict[str, Any]:
    item = _table("SITES_TABLE").get_item(Key={"site_id": site_id}).get("Item")
    if not item:
        raise LookupError(f"site {site_id} not found")
    return item


def _nearby_cooling(site: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        return cooling.nearest(float(site["lat"]), float(site["lon"]), COOLING_LIMIT)
    except Exception:
        # A cooling lookup must never block the plan; the app shows the list only when there is one.
        log.exception("cooling lookup failed; the plan goes out without cooling points")
        return []


def build_plan(site_id: str, day: str) -> None:
    site = _site(site_id)
    hourly = forecast.get_hourly(float(site["lat"]), float(site["lon"]), day)
    score = risk.score_hours(hourly, bool(site["direct_sun"]), site["shift_start"], site["shift_end"])

    try:
        plan_text, voice_text = agent.write_texts(score, site["language"])
        if not (guard.grounded([plan_text, voice_text], score) and guard.within_limits(plan_text, voice_text)):
            raise ValueError("the agent's text broke the output rules")
    except Exception:
        log.exception("agent text rejected; using the template for site %s on %s", site_id, day)
        plan_text, voice_text = guard.template(score, site["language"])

    today = _now().date()
    source = "replay" if date.fromisoformat(day) < today else "forecast"
    _set(
        site_id,
        day,
        status="ready",
        source=source,
        hours=score["hours"],
        stop_window=score["stop_window"],
        max_band=score["max_band"],
        plan_text=plan_text,
        voice_text=voice_text,
        cooling_points=_nearby_cooling(site),
        audio_status="none",
    )


def build_voice(site_id: str, day: str) -> None:
    plan = _table("PLANS_TABLE").get_item(Key={"site_id": site_id, "date": day}).get("Item")
    if not plan or plan.get("status") != "ready":
        raise LookupError("the plan is not ready to be voiced")
    key = voice.make_voice_note(plan["voice_text"], VOICE_LANGUAGE)
    _set(site_id, day, audio_status="ready", audio_s3_key=key)


def run_daily() -> dict[str, int]:
    """Rebuild today's plan for every site. One site's failure does not stop the others."""
    today = _now().date().isoformat()
    built = failed = 0
    scan: dict[str, Any] = {}
    while True:
        page = _table("SITES_TABLE").scan(**scan)
        for item in page.get("Items", []):
            try:
                build_plan(item["site_id"], today)
                built += 1
            except Exception:
                log.exception("daily plan failed for site %s", item["site_id"])
                failed += 1
                _mark_failed(item["site_id"], today)
        if "LastEvaluatedKey" not in page:
            break
        scan["ExclusiveStartKey"] = page["LastEvaluatedKey"]
    return {"built": built, "failed": failed}


def _mark_failed(site_id: str, day: str) -> None:
    try:
        _set(site_id, day, status="failed")
    except Exception:
        log.exception("could not mark plan %s/%s as failed", site_id, day)


def handler(event: dict, context: object) -> dict:
    if event.get("all_sites"):
        return run_daily()

    site_id, day, mode = event["site_id"], event["date"], event["mode"]
    try:
        if mode == "plan":
            build_plan(site_id, day)
        elif mode == "voice":
            build_voice(site_id, day)
        else:
            raise ValueError(f"unknown mode {mode!r}")
    except Exception:
        log.exception("planner failed: mode=%s site_id=%s date=%s", mode, site_id, day)
        if mode == "plan":
            _mark_failed(site_id, day)
        else:
            _set_audio_failed(site_id, day)
    return {"ok": True}


def _set_audio_failed(site_id: str, day: str) -> None:
    try:
        _set(site_id, day, audio_status="failed")
    except Exception:
        log.exception("could not mark voice note %s/%s as failed", site_id, day)
