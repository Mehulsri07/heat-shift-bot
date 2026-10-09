"""Heat risk engine: heat index, bands, direct-sun bump and stop window. Pure Python, no I/O.

The model never decides a band, a temperature or a time. This module does, and the app only shows its output.
"""

from __future__ import annotations

from typing import Any

BANDS = ("SAFE", "CAUTION", "EXTREME_CAUTION", "DANGER", "EXTREME_DANGER")

# Heat index lower bounds (°C) for CAUTION, EXTREME_CAUTION, DANGER, EXTREME_DANGER. NWS four-tier scale.
HEAT_INDEX_FLOORS = (27.0, 32.0, 39.0, 52.0)
# Air temperature lower bounds (°C). IMD plains heatwave criteria, with the 42 °C step from PLAN.md.
AIR_TEMP_FLOORS = (40.0, 42.0, 45.0, 47.0)
# A band at or above this index is a Danger-or-worse hour: it counts for the stop window and the red flag.
STOP_FROM = BANDS.index("DANGER")
DIRECT_SUN_BUMP = 1


def heat_index_c(temp_c: float, rh: float) -> float:
    """NWS heat index (Rothfusz + adjustments). Input/output in Celsius."""
    t = temp_c * 9 / 5 + 32
    hi = 0.5 * (t + 61.0 + (t - 68.0) * 1.2 + rh * 0.094)
    if hi >= 80:
        hi = (-42.379 + 2.04901523 * t + 10.14333127 * rh - 0.22475541 * t * rh
              - 0.00683783 * t * t - 0.05481717 * rh * rh + 0.00122874 * t * t * rh
              + 0.00085282 * t * rh * rh - 0.00000199 * t * t * rh * rh)
        if rh < 13 and 80 <= t <= 112:
            hi -= ((13 - rh) / 4) * ((17 - abs(t - 95)) / 17) ** 0.5
        elif rh > 85 and 80 <= t <= 87:
            hi += ((rh - 85) / 10) * ((87 - t) / 5)
    return (hi - 32) * 5 / 9


def _steps_passed(value: float, floors: tuple[float, ...]) -> int:
    return sum(value >= floor for floor in floors)


def band_for(heat_index: float, temp_c: float, direct_sun: bool) -> str:
    """The higher of the heat-index band and the air-temperature band, raised one step in direct sun."""
    index = max(_steps_passed(heat_index, HEAT_INDEX_FLOORS), _steps_passed(temp_c, AIR_TEMP_FLOORS))
    if direct_sun:
        index = min(index + DIRECT_SUN_BUMP, len(BANDS) - 1)
    return BANDS[index]


def _hour_minutes(hhmm: str) -> int:
    return int(hhmm[:2]) * 60 + int(hhmm[3:5])


def _format_hour(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def stop_window(hours: list[dict[str, Any]]) -> dict[str, str] | None:
    """Longest run of Danger-or-worse hours, as start and end (end is the end of the last hour)."""
    best: tuple[int, int] | None = None  # (start minute, end minute); the first of equal runs wins
    run: tuple[int, int] | None = None  # the run being built
    for item in hours:
        start = _hour_minutes(item["hour"])
        if BANDS.index(item["band"]) < STOP_FROM:
            run = None
            continue
        # A run continues only while the hours are back to back.
        run = (run[0], start + 60) if run is not None and run[1] == start else (start, start + 60)
        if best is None or run[1] - run[0] > best[1] - best[0]:
            best = run
    if best is None:
        return None
    return {"start": _format_hour(best[0]), "end": _format_hour(best[1])}


def score_hours(hours: list[dict[str, Any]], direct_sun: bool, shift_start: str, shift_end: str) -> dict[str, Any]:
    """Score every forecast hour inside the shift. `hours` are {"hour", "temp_c", "rh"} from forecast.get_hourly."""
    inside = [item for item in hours if shift_start <= item["hour"] < shift_end]
    if not inside:
        raise ValueError("no forecast hours fall inside the shift")

    scored = []
    for item in inside:
        index = heat_index_c(item["temp_c"], item["rh"])
        scored.append({
            "hour": item["hour"],
            "temp_c": item["temp_c"],
            "rh": item["rh"],
            "heat_index_c": round(index, 1),
            "band": band_for(index, item["temp_c"], direct_sun),
        })

    max_band = max((item["band"] for item in scored), key=BANDS.index)
    return {"hours": scored, "stop_window": stop_window(scored), "max_band": max_band}
