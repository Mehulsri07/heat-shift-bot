"""Open-Meteo forecast and archive client.

Contract:
    forecast.get_hourly(lat, lon, date) -> list[dict]
    Returns exactly 24 hourly records for the requested local date in Asia/Kolkata.
    Each record: {"hour": "HH:MM", "temp_c": float, "rh": float}.
    Raises ForecastError on any failure.

Uses the Open-Meteo Forecast API for current/future dates and the Archive API
for historical dates.  Always requests timezone=Asia/Kolkata so timestamps are
local.  Does NOT compute heat index, risk bands, or safety actions (those
belong to risk.py).
"""

import re
from datetime import date, datetime, timedelta, timezone

import requests

# Open-Meteo endpoints.
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# India Standard Time: UTC+05:30, no DST.
_IST = timezone(timedelta(hours=5, minutes=30))

# The forecast API supports ~16 days ahead; we use a conservative limit.
_MAX_FORECAST_DAYS = 16

# HTTP request timeout in seconds.
_TIMEOUT = 15

# Expected hourly variables.
_HOURLY_VARS = "temperature_2m,relative_humidity_2m"
_TIMEZONE = "Asia/Kolkata"

# Date format regex.
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class ForecastError(Exception):
    """Raised for any forecast retrieval or validation failure."""


def _validate_coords(lat: float, lon: float) -> None:
    """Validate latitude and longitude ranges."""
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        raise ForecastError(f"Invalid latitude type: {type(lat).__name__}")
    if not isinstance(lon, (int, float)) or isinstance(lon, bool):
        raise ForecastError(f"Invalid longitude type: {type(lon).__name__}")
    if not (-90 <= lat <= 90):
        raise ForecastError(f"Latitude out of range: {lat}")
    if not (-180 <= lon <= 180):
        raise ForecastError(f"Longitude out of range: {lon}")


def _validate_date(date_str: str) -> date:
    """Validate and parse a YYYY-MM-DD date string."""
    if not isinstance(date_str, str):
        raise ForecastError(f"Invalid date type: {type(date_str).__name__}")
    if not _DATE_RE.fullmatch(date_str):
        raise ForecastError(f"Invalid date format: {date_str!r}")
    try:
        return date.fromisoformat(date_str)
    except ValueError as exc:
        raise ForecastError(f"Invalid date: {date_str!r}") from exc


def _select_endpoint(requested: date) -> str:
    """Choose forecast or archive endpoint based on the requested date.

    The forecast API serves current and future dates (up to ~16 days ahead).
    The archive API serves historical dates (before today).
    """
    today = datetime.now(_IST).date()
    if requested <= today:
        # Today and past dates use archive for consistency; Open-Meteo archive
        # API covers up to yesterday, but also serves recent days.
        # For today, the forecast API is needed because archive may lag.
        if requested < today:
            return _ARCHIVE_URL
        # Today: use forecast endpoint.
        return _FORECAST_URL
    # Future dates.
    days_ahead = (requested - today).days
    if days_ahead > _MAX_FORECAST_DAYS:
        raise ForecastError(
            f"Date {requested.isoformat()} is {days_ahead} days ahead; "
            f"forecast API supports up to ~{_MAX_FORECAST_DAYS} days"
        )
    return _FORECAST_URL


def _fetch(url: str, params: dict) -> dict:
    """Make an HTTP GET request and return parsed JSON."""
    try:
        resp = requests.get(url, params=params, timeout=_TIMEOUT)
    except requests.Timeout as exc:
        raise ForecastError(f"Request timed out: {url}") from exc
    except requests.RequestException as exc:
        raise ForecastError(f"Request failed: {exc}") from exc

    if resp.status_code != 200:
        raise ForecastError(
            f"HTTP {resp.status_code} from {url}: {resp.text[:200]}"
        )

    try:
        data = resp.json()
    except ValueError as exc:
        raise ForecastError(f"Invalid JSON from {url}") from exc

    if not isinstance(data, dict):
        raise ForecastError(f"Expected JSON object, got {type(data).__name__}")

    # Open-Meteo returns an "error" key on bad requests.
    if "error" in data:
        raise ForecastError(
            f"Open-Meteo error: {data.get('reason', data['error'])}"
        )

    return data


def _parse_hourly(data: dict, date_str: str) -> list[dict]:
    """Extract and validate 24 hourly records for the requested date."""
    hourly = data.get("hourly")
    if not isinstance(hourly, dict):
        raise ForecastError("Response missing 'hourly' object")

    times = hourly.get("time")
    temps = hourly.get("temperature_2m")
    rhs = hourly.get("relative_humidity_2m")

    if times is None:
        raise ForecastError("Response missing 'hourly.time'")
    if temps is None:
        raise ForecastError("Response missing 'hourly.temperature_2m'")
    if rhs is None:
        raise ForecastError("Response missing 'hourly.relative_humidity_2m'")

    if not isinstance(times, list) or not isinstance(temps, list) or not isinstance(rhs, list):
        raise ForecastError("Hourly arrays must be lists")

    if len(times) != len(temps) or len(times) != len(rhs):
        raise ForecastError(
            f"Hourly array length mismatch: "
            f"time={len(times)}, temperature_2m={len(temps)}, "
            f"relative_humidity_2m={len(rhs)}"
        )

    # Filter to the requested date and build output records.
    prefix = date_str + "T"
    records: list[dict] = []
    for i, ts in enumerate(times):
        if not isinstance(ts, str):
            raise ForecastError(f"Malformed timestamp at index {i}: {ts!r}")
        if not ts.startswith(prefix):
            continue

        # Extract HH:MM from the timestamp (format: YYYY-MM-DDTHH:MM).
        try:
            hour_str = ts[len(prefix):]
            if len(hour_str) != 5 or hour_str[2] != ":":
                raise ForecastError(f"Malformed timestamp: {ts!r}")
        except (IndexError, ValueError) as exc:
            raise ForecastError(f"Malformed timestamp: {ts!r}") from exc

        temp = temps[i]
        rh = rhs[i]

        if temp is None or not isinstance(temp, (int, float)):
            raise ForecastError(
                f"Invalid temperature at {ts}: {temp!r}"
            )
        if rh is None or not isinstance(rh, (int, float)):
            raise ForecastError(
                f"Invalid humidity at {ts}: {rh!r}"
            )

        records.append({
            "hour": hour_str,
            "temp_c": float(temp),
            "rh": float(rh),
        })

    if len(records) != 24:
        raise ForecastError(
            f"Expected 24 hourly records for {date_str}, got {len(records)}"
        )

    return records


def get_hourly(lat: float, lon: float, date: str) -> list[dict]:
    """Fetch 24 hourly weather records for a location and date.

    Args:
        lat: Latitude (-90 to 90).
        lon: Longitude (-180 to 180).
        date: Date in YYYY-MM-DD format (Asia/Kolkata local date).

    Returns:
        List of 24 dicts, each with:
            hour: str  - local time in HH:MM format
            temp_c: float  - air temperature in Celsius
            rh: float  - relative humidity percentage

    Raises:
        ForecastError: On any failure (invalid input, network error,
            invalid response, missing data, etc.).
    """
    _validate_coords(lat, lon)
    requested = _validate_date(date)
    url = _select_endpoint(requested)

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": _HOURLY_VARS,
        "timezone": _TIMEZONE,
        "start_date": date,
        "end_date": date,
    }

    data = _fetch(url, params)
    return _parse_hourly(data, date)
