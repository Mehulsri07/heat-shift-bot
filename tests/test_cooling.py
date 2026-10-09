"""Tests for cooling.py — the nearest cooling-point lookup.

All tests use mocked DynamoDB.  No AWS infrastructure required.
"""

import math
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from cooling import CoolingError, nearest, haversine_km, _EARTH_RADIUS_KM

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------

# Jaipur city-centre reference point.
REF_LAT, REF_LON = 26.9124, 75.7873

# Sample cooling points matching the DynamoDB schema.
# Distances are pre-calculated against REF_LAT/REF_LON using the Haversine formula.
POINT_A = {
    "city": "jaipur",
    "point_id": "sms-hospital",
    "name": "SMS Hospital",
    "lat": Decimal("26.9056"),
    "lon": Decimal("75.8155"),
    "type": "clinic",
    "verified_by": "test",
}

POINT_B = {
    "city": "jaipur",
    "point_id": "central-park",
    "name": "Central Park",
    "lat": Decimal("26.9040"),
    "lon": Decimal("75.8089"),
    "type": "shade",
    "verified_by": "test",
}

POINT_C = {
    "city": "jaipur",
    "point_id": "railway-station",
    "name": "Jaipur Railway Station",
    "lat": Decimal("26.9208"),
    "lon": Decimal("75.7866"),
    "type": "water",
    "verified_by": "test",
}

POINT_D = {
    "city": "jaipur",
    "point_id": "jawahar-circle",
    "name": "Jawahar Circle",
    "lat": Decimal("26.8404"),
    "lon": Decimal("75.8003"),
    "type": "shade",
    "verified_by": "test",
}

POINT_E = {
    "city": "jaipur",
    "point_id": "kanwatia-hospital",
    "name": "Kanwatia Hospital",
    "lat": Decimal("26.9312"),
    "lon": Decimal("75.7972"),
    "type": "clinic",
    "verified_by": "test",
}

ALL_POINTS = [POINT_A, POINT_B, POINT_C, POINT_D, POINT_E]


def _expected_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Independently calculate Haversine distance for verification."""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(6371.0 * c, 2)


class FakeTable:
    """Mock DynamoDB table that supports query with pagination."""

    def __init__(self, items: list[dict], page_size: int | None = None) -> None:
        self._items = items
        self._page_size = page_size  # None = no pagination

    def query(self, **kwargs) -> dict:
        # Filter to matching city
        start = kwargs.get("ExclusiveStartKey")
        items = list(self._items)

        if start:
            # Find position after the start key
            idx = next(
                (i for i, item in enumerate(items)
                 if item.get("city") == start.get("city") and item.get("point_id") == start.get("point_id")),
                -1,
            )
            items = items[idx + 1:]

        if self._page_size and len(items) > self._page_size:
            page = items[:self._page_size]
            last = {"city": page[-1]["city"], "point_id": page[-1]["point_id"]}
            return {"Items": page, "LastEvaluatedKey": last}
        return {"Items": items}


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COOLING_TABLE", "test-cooling-table")


def _mock_dynamo(monkeypatch: pytest.MonkeyPatch, items: list[dict],
                 page_size: int | None = None) -> None:
    """Patch boto3 to return a FakeTable."""
    fake = FakeTable(items, page_size)
    mock_resource = MagicMock()
    mock_resource.Table.return_value = fake
    monkeypatch.setattr("cooling.boto3.resource", lambda *a, **kw: mock_resource)


# ---------------------------------------------------------------------------
# Default limit (3)
# ---------------------------------------------------------------------------

class TestDefaultLimit:
    def test_returns_at_most_three(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, ALL_POINTS)
        result = nearest(REF_LAT, REF_LON)
        assert len(result) == 3

    def test_returns_fewer_if_less_than_three_exist(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, [POINT_A])
        result = nearest(REF_LAT, REF_LON)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Custom limits
# ---------------------------------------------------------------------------

class TestCustomLimits:
    def test_limit_one(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, ALL_POINTS)
        result = nearest(REF_LAT, REF_LON, limit=1)
        assert len(result) == 1

    def test_limit_five(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, ALL_POINTS)
        result = nearest(REF_LAT, REF_LON, limit=5)
        assert len(result) == 5

    def test_limit_exceeds_total(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, [POINT_A, POINT_B])
        result = nearest(REF_LAT, REF_LON, limit=10)
        assert len(result) == 2


# ---------------------------------------------------------------------------
# Ordering
# ---------------------------------------------------------------------------

class TestOrdering:
    def test_nearest_first(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, ALL_POINTS)
        result = nearest(REF_LAT, REF_LON, limit=5)
        distances = [r["distance_km"] for r in result]
        assert distances == sorted(distances)

    def test_correct_nearest_point(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, ALL_POINTS)
        result = nearest(REF_LAT, REF_LON, limit=1)
        # The railway station is closest to our reference point.
        assert result[0]["name"] == "Jaipur Railway Station"


# ---------------------------------------------------------------------------
# Haversine distance calculations
# ---------------------------------------------------------------------------

class TestHaversineDistances:
    def test_known_distance_sms_hospital(self) -> None:
        """SMS Hospital is about 3.2 km from reference point."""
        dist = haversine_km(REF_LAT, REF_LON, 26.9056, 75.8155)
        expected = _expected_distance(REF_LAT, REF_LON, 26.9056, 75.8155)
        assert abs(dist - expected) < 0.01

    def test_known_distance_jawahar_circle(self) -> None:
        """Jawahar Circle is about 8.2 km from reference point."""
        dist = haversine_km(REF_LAT, REF_LON, 26.8404, 75.8003)
        expected = _expected_distance(REF_LAT, REF_LON, 26.8404, 75.8003)
        assert abs(dist - expected) < 0.01

    def test_same_point_is_zero(self) -> None:
        assert haversine_km(REF_LAT, REF_LON, REF_LAT, REF_LON) == 0.0

    def test_antipodal_distance(self) -> None:
        """Opposite side of Earth is half circumference."""
        dist = haversine_km(0, 0, 0, 180)
        assert abs(dist - math.pi * _EARTH_RADIUS_KM) < 1.0

    def test_distance_matches_output(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        """Verify that distance_km in output matches independent calculation."""
        _mock_dynamo(monkeypatch, ALL_POINTS)
        result = nearest(REF_LAT, REF_LON, limit=5)
        for r in result:
            expected = _expected_distance(REF_LAT, REF_LON, r["lat"], r["lon"])
            assert abs(r["distance_km"] - expected) < 0.01, f"Mismatch for {r['name']}"


# ---------------------------------------------------------------------------
# Output fields and types
# ---------------------------------------------------------------------------

class TestOutputFields:
    def test_required_keys(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, [POINT_A])
        result = nearest(REF_LAT, REF_LON)
        assert set(result[0].keys()) == {"name", "type", "lat", "lon", "distance_km"}

    def test_numeric_types(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, [POINT_A])
        result = nearest(REF_LAT, REF_LON)
        assert isinstance(result[0]["lat"], float)
        assert isinstance(result[0]["lon"], float)
        assert isinstance(result[0]["distance_km"], float)

    def test_string_fields(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, [POINT_A])
        result = nearest(REF_LAT, REF_LON)
        assert isinstance(result[0]["name"], str)
        assert isinstance(result[0]["type"], str)


# ---------------------------------------------------------------------------
# Empty results
# ---------------------------------------------------------------------------

class TestEmptyResults:
    def test_no_points_returns_empty_list(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        _mock_dynamo(monkeypatch, [])
        result = nearest(REF_LAT, REF_LON)
        assert result == []


# ---------------------------------------------------------------------------
# Invalid inputs
# ---------------------------------------------------------------------------

class TestInvalidInputs:
    def test_invalid_latitude_high(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Latitude out of range"):
            nearest(91.0, REF_LON)

    def test_invalid_latitude_low(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Latitude out of range"):
            nearest(-91.0, REF_LON)

    def test_invalid_longitude(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Longitude out of range"):
            nearest(REF_LAT, 181.0)

    def test_invalid_latitude_bool(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Invalid latitude type"):
            nearest(True, REF_LON)  # type: ignore

    def test_invalid_longitude_bool(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Invalid longitude type"):
            nearest(REF_LAT, False)  # type: ignore

    def test_invalid_limit_zero(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Limit must be at least 1"):
            nearest(REF_LAT, REF_LON, limit=0)

    def test_invalid_limit_negative(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Limit must be at least 1"):
            nearest(REF_LAT, REF_LON, limit=-1)

    def test_invalid_limit_bool(self, mock_env: None) -> None:
        with pytest.raises(CoolingError, match="Invalid limit type"):
            nearest(REF_LAT, REF_LON, limit=True)  # type: ignore

    def test_missing_cooling_table(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("COOLING_TABLE", raising=False)
        with pytest.raises(CoolingError, match="COOLING_TABLE"):
            nearest(REF_LAT, REF_LON)


# ---------------------------------------------------------------------------
# Malformed records
# ---------------------------------------------------------------------------

class TestMalformedRecords:
    def test_missing_lat_is_skipped(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        bad = {"city": "jaipur", "point_id": "bad", "name": "Bad", "lon": Decimal("75.8"), "type": "water", "verified_by": "test"}
        _mock_dynamo(monkeypatch, [bad, POINT_A])
        result = nearest(REF_LAT, REF_LON)
        assert len(result) == 1
        assert result[0]["name"] == "SMS Hospital"

    def test_missing_name_is_skipped(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        bad = {"city": "jaipur", "point_id": "bad", "lat": Decimal("26.9"), "lon": Decimal("75.8"), "type": "water", "verified_by": "test"}
        _mock_dynamo(monkeypatch, [bad, POINT_A])
        result = nearest(REF_LAT, REF_LON)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# DynamoDB errors
# ---------------------------------------------------------------------------

class TestDynamoDBErrors:
    def test_dynamo_client_error(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        mock_resource = MagicMock()
        mock_table = MagicMock()
        mock_table.query.side_effect = Exception("DynamoDB is down")
        mock_resource.Table.return_value = mock_table
        monkeypatch.setattr("cooling.boto3.resource", lambda *a, **kw: mock_resource)
        with pytest.raises(CoolingError, match="DynamoDB error"):
            nearest(REF_LAT, REF_LON)


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

class TestPagination:
    def test_paginated_results(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        """Simulates a paginated DynamoDB response (page size 2)."""
        _mock_dynamo(monkeypatch, ALL_POINTS, page_size=2)
        result = nearest(REF_LAT, REF_LON, limit=5)
        assert len(result) == 5
        # Verify correct ordering
        distances = [r["distance_km"] for r in result]
        assert distances == sorted(distances)


# ---------------------------------------------------------------------------
# Equal distances (stability)
# ---------------------------------------------------------------------------

class TestEqualDistances:
    def test_stable_sort_for_equal_distances(self, monkeypatch: pytest.MonkeyPatch, mock_env: None) -> None:
        """Two points at equal distance should both appear, in stable order."""
        # Create two points at the same coordinates
        p1 = {**POINT_A, "point_id": "equal-1", "name": "Equal One"}
        p2 = {**POINT_A, "point_id": "equal-2", "name": "Equal Two"}
        _mock_dynamo(monkeypatch, [p1, p2])
        result = nearest(REF_LAT, REF_LON, limit=2)
        assert len(result) == 2
        assert result[0]["distance_km"] == result[1]["distance_km"]
        # Stable sort preserves insertion order.
        assert result[0]["name"] == "Equal One"
        assert result[1]["name"] == "Equal Two"
