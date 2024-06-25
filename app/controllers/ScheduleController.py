import os
import json
from datetime import datetime, timedelta, time
import boto3
from app.localization import timezone
from app.models import ElectricityStateLog


def preload_s3_data():
    client = boto3.client("s3")
    result = client.get_object(Bucket=os.getenv("SCHEDULE_BUCKET"), Key="schedule.json")
    raw_json = result["Body"].read().decode("utf-8")
    return json.loads(raw_json)


SCHEDULE = preload_s3_data()


class ScheduleController:

    def __init__(self) -> None:
        self.tz = timezone

    def _process_schedule(self, week_day: int, group: str):
        today_schedule: dict[str, str] = SCHEDULE[group][str(week_day + 1)]
        tomorrow_schedule: dict[str, str] = SCHEDULE[group][str((week_day + 1) % 7 + 1)]
        today_agg = [today_schedule[str(i)] for i in range(1, 25)]
        tomorrow_agg = [tomorrow_schedule[str(i)] for i in range(1, 25)]
        return today_agg + tomorrow_agg

    def _next_zones_forecast(self, group: str):
        now = datetime.now(self.tz)
        week_day = now.weekday()
        now_hour = now.hour
        linear_schedule = self._process_schedule(week_day, group)
        result = []
        zone_type = linear_schedule[now_hour]
        zone_start = datetime.combine(
            now.date(), time(0, 0, 0, 0, tzinfo=self.tz)
        ) + timedelta(hours=now_hour)
        zone_end = None
        while len(result) < 3:
            now_hour += 1
            if zone_type != linear_schedule[now_hour]:
                zone_end = datetime.combine(
                    now.date(), time(0, 0, 0, 0, tzinfo=self.tz)
                ) + timedelta(hours=now_hour)
                result.append(
                    {
                        "name": zone_type,
                        "start": zone_start,
                        "end": zone_end,
                    }
                )
                zone_type = linear_schedule[now_hour]
                zone_start = zone_end
        return result

    def get_next_zones_forecast(self, group: str):
        result = self._next_zones_forecast(group)
        result.pop(0)
        return result

    def get_state(self, group: str) -> ElectricityStateLog.STATE:
        STATE = ElectricityStateLog.STATE
        now = datetime.now(self.tz)
        weekday = now.weekday()
        schedule = SCHEDULE[group][str(weekday + 1)]
        state_translation = dict(yes=STATE.ON, no=STATE.OFF, maybe=STATE.UNKNOWN)
        forecast = self._next_zones_forecast(group)
        this_period = forecast[0]
        return state_translation[schedule[str(now.time().hour + 1)]], this_period["end"]


if __name__ == "__main__":
    schedule = ScheduleController()
    print(schedule.next_black_zone_datetime(group="1"))
