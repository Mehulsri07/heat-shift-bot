"""Tests for forecast.py — the Open-Meteo client.

All unit tests use mocked HTTP responses.  No network access required.
The integration test at the bottom is marked with @pytest.mark.integration and
is skipped by default; run ``pytest -m integration`` to hit the live API.
"""

import json
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

import pytest
import requests as _requests_lib

from forecast import ForecastError, get_hourly, _FORECAST_URL, _ARCHIVE_URL, _IST

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Jaipur coordinates for test fixtures.
LAT, LON = 26.9124, 75.7873
DATE_STR = "2025-05-20"  # a historical date

def _make_hourly(date_str: str, temps: list | None = None, rhs: list | None = None) -> dict:
    """Build a valid Open-Meteo response for a single day with 24 hours."""
    if temps is None:
        temps = [30.0 + i * 0.5 for i in range(24)]
    if rhs is None:
        rhs = [50 + i for i in range(24)]
    times = [f"{date_str}T{h:02d}:00" for h in range(24)]
    return {
        "hourly": {
            "time": times,
            "temperature_2m": temps,
            "relative_humidity_2m": rhs,
        }
    }


def _mock_response(status: int = 200, json_data: dict | None = None,
                   text: str = "", raise_timeout: bool = False,
                   raise_error: bool = False, bad_json: bool = False) -> MagicMock:
    """Create a mock requests.Response."""
    mock = MagicMock(spec=_requests_lib.Response)
    mock.status_code = status
    mock.text = text or json.dumps(json_data or {})
    if bad_json:
        mock.json.side_effect = ValueError("bad json")
    elif json_data is not None:
        mock.json.return_value = json_data
    else:
        mock.json.return_value = {}
    return mock


# ---------------------------------------------------------------------------
# Valid responses
# ---------------------------------------------------------------------------

class TestValidForecastResponse:
    """Tests for successful forecast retrieval."""

    @patch("forecast.requests.get")
    def test_returns_24_records_for_valid_date(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data=_make_hourly(DATE_STR))
        result = get_hourly(LAT, LON, DATE_STR)
        assert len(result) == 24

    @patch("forecast.requests.get")
    def test_each_record_has_required_keys(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data=_make_hourly(DATE_STR))
        result = get_hourly(LAT, LON, DATE_STR)
        for rec in result:
            assert set(rec.keys()) == {"hour", "temp_c", "rh"}

    @patch("forecast.requests.get")
    def test_values_are_numeric(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data=_make_hourly(DATE_STR))
        result = get_hourly(LAT, LON, DATE_STR)
        for rec in result:
            assert isinstance(rec["temp_c"], float)
            assert isinstance(rec["rh"], float)

    @patch("forecast.requests.get")
    def test_hours_are_ordered_and_formatted(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data=_make_hourly(DATE_STR))
        result = get_hourly(LAT, LON, DATE_STR)
        hours = [r["hour"] for r in result]
        expected = [f"{h:02d}:00" for h in range(24)]
        assert hours == expected

    @patch("forecast.requests.get")
    def test_correct_temperature_values(self, mock_get: MagicMock) -> None:
        temps = [25.0 + i for i in range(24)]
        mock_get.return_value = _mock_response(json_data=_make_hourly(DATE_STR, temps=temps))
        result = get_hourly(LAT, LON, DATE_STR)
        for i, rec in enumerate(result):
            assert rec["temp_c"] == 25.0 + i

    @patch("forecast.requests.get")
    def test_correct_humidity_values(self, mock_get: MagicMock) -> None:
        rhs = [40 + i * 2 for i in range(24)]
        mock_get.return_value = _mock_response(json_data=_make_hourly(DATE_STR, rhs=rhs))
        result = get_hourly(LAT, LON, DATE_STR)
        for i, rec in enumerate(result):
            assert rec["rh"] == 40 + i * 2


# ---------------------------------------------------------------------------
# Endpoint selection
# ---------------------------------------------------------------------------

class TestEndpointSelection:
    """Tests that the correct Open-Meteo endpoint is chosen."""

    @patch("forecast.requests.get")
    def test_historical_date_uses_archive(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data=_make_hourly("2025-05-20"))
        get_hourly(LAT, LON, "2025-05-20")
        url = mock_get.call_args[0][0]
        assert url == _ARCHIVE_URL

    @patch("forecast.requests.get")
    @patch("forecast.datetime")
    def test_today_uses_forecast(self, mock_dt: MagicMock, mock_get: MagicMock) -> None:
        today_str = "2025-10-09"
        mock_dt.now.return_value = datetime(2025, 10, 9, 12, 0, tzinfo=_IST)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        mock_get.return_value = _mock_response(json_data=_make_hourly(today_str))
        get_hourly(LAT, LON, today_str)
        url = mock_get.call_args[0][0]
        assert url == _FORECAST_URL

    @patch("forecast.requests.get")
    @patch("forecast.datetime")
    def test_future_date_uses_forecast(self, mock_dt: MagicMock, mock_get: MagicMock) -> None:
        mock_dt.now.return_value = datetime(2025, 10, 9, 12, 0, tzinfo=_IST)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        future_str = "2025-10-12"
        mock_get.return_value = _mock_response(json_data=_make_hourly(future_str))
        get_hourly(LAT, LON, future_str)
        url = mock_get.call_args[0][0]
        assert url == _FORECAST_URL

    @patch("forecast.datetime")
    def test_far_future_date_raises(self, mock_dt: MagicMock) -> None:
        mock_dt.now.return_value = datetime(2025, 10, 9, 12, 0, tzinfo=_IST)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        far_future = "2025-11-15"
        with pytest.raises(ForecastError, match="days ahead"):
            get_hourly(LAT, LON, far_future)


# ---------------------------------------------------------------------------
# Timezone parameter
# ---------------------------------------------------------------------------

class TestTimezoneParam:
    """Verify that Asia/Kolkata timezone is always requested."""

    @patch("forecast.requests.get")
    def test_timezone_param_is_asia_kolkata(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data=_make_hourly(DATE_STR))
        get_hourly(LAT, LON, DATE_STR)
        params = mock_get.call_args[1].get("params") or mock_get.call_args[0][1] if len(mock_get.call_args[0]) > 1 else mock_get.call_args[1]["params"]
        assert params["timezone"] == "Asia/Kolkata"


# ---------------------------------------------------------------------------
# Invalid inputs
# ---------------------------------------------------------------------------

class TestInvalidInputs:
    """Tests for input validation."""

    def test_invalid_date_format(self) -> None:
        with pytest.raises(ForecastError, match="Invalid date"):
            get_hourly(LAT, LON, "20-05-2025")

    def test_invalid_date_value(self) -> None:
        with pytest.raises(ForecastError, match="Invalid date"):
            get_hourly(LAT, LON, "2025-13-01")

    def test_date_not_string(self) -> None:
        with pytest.raises(ForecastError, match="Invalid date type"):
            get_hourly(LAT, LON, 20250520)  # type: ignore

    def test_latitude_out_of_range_high(self) -> None:
        with pytest.raises(ForecastError, match="Latitude out of range"):
            get_hourly(91.0, LON, DATE_STR)

    def test_latitude_out_of_range_low(self) -> None:
        with pytest.raises(ForecastError, match="Latitude out of range"):
            get_hourly(-91.0, LON, DATE_STR)

    def test_longitude_out_of_range(self) -> None:
        with pytest.raises(ForecastError, match="Longitude out of range"):
            get_hourly(LAT, 181.0, DATE_STR)

    def test_latitude_bool_rejected(self) -> None:
        with pytest.raises(ForecastError, match="Invalid latitude type"):
            get_hourly(True, LON, DATE_STR)  # type: ignore

    def test_longitude_bool_rejected(self) -> None:
        with pytest.raises(ForecastError, match="Invalid longitude type"):
            get_hourly(LAT, False, DATE_STR)  # type: ignore

    def test_latitude_string_rejected(self) -> None:
        with pytest.raises(ForecastError, match="Invalid latitude type"):
            get_hourly("26.9", LON, DATE_STR)  # type: ignore

    def test_longitude_string_rejected(self) -> None:
        with pytest.raises(ForecastError, match="Invalid longitude type"):
            get_hourly(LAT, "75.8", DATE_STR)  # type: ignore


# ---------------------------------------------------------------------------
# HTTP errors
# ---------------------------------------------------------------------------

class TestHTTPErrors:
    """Tests for HTTP-level failures."""

    @patch("forecast.requests.get")
    def test_http_500_raises(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(status=500, text="Server Error")
        with pytest.raises(ForecastError, match="HTTP 500"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_http_404_raises(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(status=404, text="Not Found")
        with pytest.raises(ForecastError, match="HTTP 404"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_timeout_raises(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = _requests_lib.Timeout("timed out")
        with pytest.raises(ForecastError, match="timed out"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_connection_error_raises(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = _requests_lib.ConnectionError("connection refused")
        with pytest.raises(ForecastError, match="Request failed"):
            get_hourly(LAT, LON, DATE_STR)


# ---------------------------------------------------------------------------
# Invalid JSON / response structure
# ---------------------------------------------------------------------------

class TestInvalidResponses:
    """Tests for malformed API responses."""

    @patch("forecast.requests.get")
    def test_invalid_json_raises(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(bad_json=True)
        with pytest.raises(ForecastError, match="Invalid JSON"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_open_meteo_error_field_raises(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data={"error": True, "reason": "Bad params"})
        with pytest.raises(ForecastError, match="Open-Meteo error"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_missing_hourly_object_raises(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(json_data={"daily": {}})
        with pytest.raises(ForecastError, match="missing 'hourly'"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_missing_temperature_raises(self, mock_get: MagicMock) -> None:
        data = _make_hourly(DATE_STR)
        del data["hourly"]["temperature_2m"]
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="temperature_2m"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_missing_humidity_raises(self, mock_get: MagicMock) -> None:
        data = _make_hourly(DATE_STR)
        del data["hourly"]["relative_humidity_2m"]
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="relative_humidity_2m"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_unequal_array_lengths_raises(self, mock_get: MagicMock) -> None:
        data = _make_hourly(DATE_STR)
        data["hourly"]["temperature_2m"] = data["hourly"]["temperature_2m"][:20]
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="length mismatch"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_incomplete_hourly_data_raises(self, mock_get: MagicMock) -> None:
        """Only 20 hours instead of 24."""
        data = _make_hourly(DATE_STR)
        data["hourly"]["time"] = data["hourly"]["time"][:20]
        data["hourly"]["temperature_2m"] = data["hourly"]["temperature_2m"][:20]
        data["hourly"]["relative_humidity_2m"] = data["hourly"]["relative_humidity_2m"][:20]
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="Expected 24"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_null_temperature_value_raises(self, mock_get: MagicMock) -> None:
        data = _make_hourly(DATE_STR)
        data["hourly"]["temperature_2m"][10] = None
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="Invalid temperature"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_null_humidity_value_raises(self, mock_get: MagicMock) -> None:
        data = _make_hourly(DATE_STR)
        data["hourly"]["relative_humidity_2m"][5] = None
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="Invalid humidity"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_malformed_timestamp_raises(self, mock_get: MagicMock) -> None:
        data = _make_hourly(DATE_STR)
        data["hourly"]["time"][3] = f"{DATE_STR}T3:00"  # missing leading zero
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="Malformed timestamp"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_non_string_timestamp_raises(self, mock_get: MagicMock) -> None:
        data = _make_hourly(DATE_STR)
        data["hourly"]["time"][0] = 12345
        mock_get.return_value = _mock_response(json_data=data)
        with pytest.raises(ForecastError, match="Malformed timestamp"):
            get_hourly(LAT, LON, DATE_STR)

    @patch("forecast.requests.get")
    def test_response_is_list_not_dict_raises(self, mock_get: MagicMock) -> None:
        mock = MagicMock(spec=_requests_lib.Response)
        mock.status_code = 200
        mock.json.return_value = [1, 2, 3]
        mock.text = "[1,2,3]"
        mock_get.return_value = mock
        with pytest.raises(ForecastError, match="Expected JSON object"):
            get_hourly(LAT, LON, DATE_STR)


# ---------------------------------------------------------------------------
# Integration test (skipped by default)
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRealService:
    """Live API test — requires internet.

    Run with:  pytest -m integration tests/test_forecast.py -v

    Manual verification procedure (if pytest is unavailable):
        python3 -c "
        from forecast import get_hourly
        result = get_hourly(26.9124, 75.7873, '2025-05-20')
        for r in result:
            print(f'{r[\"hour\"]}  {r[\"temp_c\"]:5.1f}°C  {r[\"rh\"]:4.0f}%')
        print(f'Total records: {len(result)}')
        "
    """

    def test_historical_date_returns_24_records(self) -> None:
        result = get_hourly(26.9124, 75.7873, "2025-05-20")
        assert len(result) == 24
        for rec in result:
            assert "hour" in rec and "temp_c" in rec and "rh" in rec
            assert isinstance(rec["temp_c"], float)
            assert isinstance(rec["rh"], float)
