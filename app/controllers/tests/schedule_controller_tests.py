import pytest
import json
from freezegun import freeze_time

from app.models import ElectricityStateLog


@pytest.fixture
def mock_schedule_data(monkeypatch):
    with open("app/controllers/tests/fixtures/schedule.json", encoding="utf-8") as f:
        schedule = json.load(f)
        monkeypatch.setattr(
            "app.controllers.preload_s3_data",
            lambda: schedule,
        )


class TestScheduleController:
    def test_middle_of_the_day(self, mock_schedule_data):
        # Tuesday
        with freeze_time("2024-06-25 13:30:00", tz_offset=-3):
            from app.controllers import ScheduleController

            controller = ScheduleController()
            current_state, till = controller.get_state("1")
            assert current_state == ElectricityStateLog.STATE.OFF
            assert till.hour == 15
            forecast = controller.get_next_zones_forecast("1")
            assert forecast[0]["name"] == "maybe"
            assert forecast[0]["start"].hour == 15
            assert forecast[0]["end"].hour == 18
            assert forecast[1]["name"] == "yes"
            assert forecast[1]["start"].hour == 18
            assert forecast[1]["end"].hour == 21

    def test_end_of_the_day(self, mock_schedule_data):
        # Saturday
        with freeze_time("2024-06-22 23:30:00", tz_offset=-3):
            from app.controllers import ScheduleController

            controller = ScheduleController()
            controller = ScheduleController()
            current_state, till = controller.get_state("1")
            assert current_state == ElectricityStateLog.STATE.ON
            assert till.hour == 0
            forecast = controller.get_next_zones_forecast("1")
            assert forecast[0]["start"].hour == 0
            assert forecast[1]["start"].hour == 3
