"""Nearest cooling points from DynamoDB.

Contract:
    cooling.nearest(lat, lon, limit=3) -> list[dict]
    Returns the closest cooling points sorted by ascending great-circle
    distance (Haversine).  Each record: {"name", "type", "lat", "lon",
    "distance_km"}.  Returns an empty list when no points exist.

Reads from the CoolingPoints DynamoDB table configured via the COOLING_TABLE
environment variable.  Uses "jaipur" as the demo city partition key.
"""

import math
import os
from decimal import Decimal
from typing import Any

import boto3
from boto3.dynamodb.conditions import Key as DynamoKey

# Earth's mean radius in kilometres (WGS-84 derived).
_EARTH_RADIUS_KM = 6371.0

# Demo city partition key — follows existing repository conventions.
_DEMO_CITY = "jaipur"


class CoolingError(Exception):
    """Raised on DynamoDB or data errors."""


def _validate_coords(lat: float, lon: float) -> None:
    """Validate latitude and longitude ranges."""
    if not isinstance(lat, (int, float, Decimal)) or isinstance(lat, bool):
        raise CoolingError(f"Invalid latitude type: {type(lat).__name__}")
    if not isinstance(lon, (int, float, Decimal)) or isinstance(lon, bool):
        raise CoolingError(f"Invalid longitude type: {type(lon).__name__}")
    if not (-90 <= float(lat) <= 90):
        raise CoolingError(f"Latitude out of range: {lat}")
    if not (-180 <= float(lon) <= 180):
        raise CoolingError(f"Longitude out of range: {lon}")


def _validate_limit(limit: int) -> None:
    """Validate the limit parameter."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise CoolingError(f"Invalid limit type: {type(limit).__name__}")
    if limit < 1:
        raise CoolingError(f"Limit must be at least 1, got {limit}")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points using the Haversine formula.

    All inputs in decimal degrees; returns distance in kilometres.
    """
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return _EARTH_RADIUS_KM * c


def _query_points(table: Any) -> list[dict]:
    """Query all cooling points for the demo city, handling pagination."""
    items: list[dict] = []
    kwargs: dict = {
        "KeyConditionExpression": DynamoKey("city").eq(_DEMO_CITY),
    }
    while True:
        response = table.query(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
        kwargs["ExclusiveStartKey"] = last_key
    return items


def nearest(lat: float, lon: float, limit: int = 3) -> list[dict]:
    """Find the nearest cooling points to the given coordinates.

    Args:
        lat: Latitude (-90 to 90).
        lon: Longitude (-180 to 180).
        limit: Maximum number of results to return (default 3, minimum 1).

    Returns:
        List of dicts sorted by ascending distance, each with:
            name: str
            type: str  ("water", "shade", or "clinic")
            lat: float
            lon: float
            distance_km: float

    Raises:
        CoolingError: On invalid inputs or DynamoDB errors.
    """
    _validate_coords(lat, lon)
    _validate_limit(limit)

    table_name = os.environ.get("COOLING_TABLE")
    if not table_name:
        raise CoolingError("COOLING_TABLE environment variable is not set")

    try:
        table = boto3.resource("dynamodb").Table(table_name)
        items = _query_points(table)
    except CoolingError:
        raise
    except Exception as exc:
        raise CoolingError(f"DynamoDB error: {exc}") from exc

    if not items:
        return []

    results: list[dict] = []
    for item in items:
        try:
            point_lat = float(item["lat"])
            point_lon = float(item["lon"])
            name = item["name"]
            point_type = item["type"]
        except (KeyError, TypeError, ValueError) as exc:
            # Skip malformed records rather than crashing the whole query,
            # but log implicitly via the exception chain if re-raised.
            continue

        dist = haversine_km(float(lat), float(lon), point_lat, point_lon)
        results.append({
            "name": name,
            "type": point_type,
            "lat": point_lat,
            "lon": point_lon,
            "distance_km": round(dist, 2),
        })

    # Sort by distance (stable sort preserves insertion order for equal distances).
    results.sort(key=lambda p: p["distance_km"])
    return results[:limit]
