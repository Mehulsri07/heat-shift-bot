"""Risk engine: heat index, bands, direct-sun bump and stop window.

Every hour and number below is a made-up TEST FIXTURE, not real forecast data.

Heat index: the expected values come from the NWS Rothfusz regression with its adjustments, as written in
src/risk.py. They are regression values, not yet read off the NWS chart. Checking them against the chart is still
open for the risk owner (see PLAN.md, Heat risk engine).
"""

import pytest

import risk


def hours(*rows: tuple[str, float, float]) -> list[dict]:
    return [{"hour": hour, "temp_c": temp, "rh": rh} for hour, temp, rh in rows]


@pytest.mark.parametrize("temp_c,rh,expected", [
    (30, 40, 29.7),
    (37, 70, 58.2),
    (35, 60, 45.1),
    (40, 30, 43.1),
    (46, 20, 49.0),
])
def test_heat_index_matches_the_regression_values(temp_c: float, rh: float, expected: float) -> None:
    assert risk.heat_index_c(temp_c, rh) == pytest.approx(expected, abs=0.05)


def test_heat_index_is_below_air_temperature_in_dry_air() -> None:
    # The reason both columns are needed: in dry air the heat index can read below the air temperature.
    assert risk.heat_index_c(45, 0) < 45


@pytest.mark.parametrize("heat_index,temp_c,band", [
    (26.9, 0, "SAFE"),
    (27.0, 0, "CAUTION"),
    (31.9, 0, "CAUTION"),
    (32.0, 0, "EXTREME_CAUTION"),
    (38.9, 0, "EXTREME_CAUTION"),
    (39.0, 0, "DANGER"),
    (51.9, 0, "DANGER"),
    (52.0, 0, "EXTREME_DANGER"),
    (0, 39.9, "SAFE"),
    (0, 40.0, "CAUTION"),
    (0, 41.9, "CAUTION"),
    (0, 42.0, "EXTREME_CAUTION"),
    (0, 44.9, "EXTREME_CAUTION"),
    (0, 45.0, "DANGER"),
    (0, 46.9, "DANGER"),
    (0, 47.0, "EXTREME_DANGER"),
])
def test_every_band_boundary(heat_index: float, temp_c: float, band: str) -> None:
    assert risk.band_for(heat_index, temp_c, direct_sun=False) == band


def test_dry_air_is_banded_by_the_air_temperature() -> None:
    # 45 °C at 0% humidity: the heat index is 38.8 (EXTREME_CAUTION), but the air temperature is DANGER.
    index = risk.heat_index_c(45, 0)
    assert risk.band_for(index, 45, direct_sun=False) == "DANGER"


@pytest.mark.parametrize("heat_index,temp_c,band", [
    (20, 33, "CAUTION"),          # SAFE by heat index and by temperature, raised one step
    (30, 35, "EXTREME_CAUTION"),  # CAUTION raised one step
    (60, 50, "EXTREME_DANGER"),   # already the top band: the bump stops there
])
def test_direct_sun_raises_a_band_by_one_and_stops_at_the_top(heat_index: float, temp_c: float, band: str) -> None:
    assert risk.band_for(heat_index, temp_c, direct_sun=True) == band


def test_score_hours_keeps_only_the_shift() -> None:
    rows = hours(("06:00", 30, 40), ("07:00", 30, 40), ("17:00", 30, 40), ("18:00", 46, 20))
    scored = risk.score_hours(rows, direct_sun=False, shift_start="07:00", shift_end="18:00")
    assert [item["hour"] for item in scored["hours"]] == ["07:00", "17:00"]


def test_score_hours_outputs_the_fields_the_api_returns() -> None:
    scored = risk.score_hours(hours(("14:00", 46, 20)), False, "07:00", "18:00")
    item = scored["hours"][0]
    assert set(item) == {"hour", "temp_c", "rh", "heat_index_c", "band"}
    assert item["heat_index_c"] == round(risk.heat_index_c(46, 20), 1)
    assert item["band"] == "DANGER" and scored["max_band"] == "DANGER"


def test_score_hours_refuses_an_empty_shift() -> None:
    with pytest.raises(ValueError):
        risk.score_hours(hours(("06:00", 30, 40)), False, "07:00", "18:00")


def test_stop_window_is_the_end_of_the_last_hour() -> None:
    rows = hours(("11:00", 30, 40), ("12:00", 46, 20), ("13:00", 46, 20), ("14:00", 46, 20), ("15:00", 46, 20),
                 ("16:00", 30, 40))
    scored = risk.score_hours(rows, False, "07:00", "18:00")
    assert scored["stop_window"] == {"start": "12:00", "end": "16:00"}


def test_stop_window_takes_the_longest_run() -> None:
    rows = hours(("10:00", 46, 20), ("11:00", 30, 40), ("12:00", 46, 20), ("13:00", 46, 20), ("14:00", 46, 20))
    scored = risk.score_hours(rows, False, "07:00", "18:00")
    assert scored["stop_window"] == {"start": "12:00", "end": "15:00"}


def test_stop_window_is_none_without_danger_hours() -> None:
    rows = hours(("12:00", 30, 40), ("13:00", 30, 40))
    assert risk.score_hours(rows, False, "07:00", "18:00")["stop_window"] is None


def test_runs_with_a_gap_are_not_joined() -> None:
    rows = hours(("12:00", 46, 20), ("14:00", 46, 20))
    assert risk.stop_window(risk.score_hours(rows, False, "07:00", "18:00")["hours"]) == {
        "start": "12:00", "end": "13:00"}


def test_direct_sun_can_create_a_stop_window() -> None:
    # 35 °C at 40% is EXTREME_CAUTION in shade and DANGER in direct sun, so only the sunny site stops work.
    rows = hours(("13:00", 35, 40))
    assert risk.score_hours(rows, False, "07:00", "18:00")["stop_window"] is None
    assert risk.score_hours(rows, True, "07:00", "18:00")["stop_window"] == {"start": "13:00", "end": "14:00"}
