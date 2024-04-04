import os
import json
from typing import Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import pytz
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

    def aggregate_day_schedule(self, weekday: int, group: str):
        day_schedule: dict[str,
                           str] = SCHEDULE[group][str(weekday + 1)]
        aggregated_day_schedule: dict[str, list[int]] = dict()

        schedule_pairs = sorted([(value, int(key)-1)
                                 for key, value in day_schedule.items()], key=lambda d: d[1])
        aggregated_day_schedule = defaultdict(list)
        helper = defaultdict(list)

        for state, hour in schedule_pairs:
            aggregated_day_schedule[state].append(hour)
            array = aggregated_day_schedule[state]
            length = len(array)
            helper[state].append(0 if length == 1 else (array[-1] - array[-2]))

        for state, timing in aggregated_day_schedule.items():
            new_timing = [timing[i] if helper[state][i] != 1 else None
                          for i in range(len(timing))]
            aggregated_day_schedule[state] = list(
                filter(lambda i: i, new_timing))

        return aggregated_day_schedule
    
    def _next_zone_datetime_by_type(self, group: str, zone_type: str) -> datetime:
        now = datetime.now(self.tz)
        day_of_week = now.weekday()
        hour = now.time().hour

        today_schedule = self.aggregate_day_schedule(day_of_week, group)
        tomorrow_schedule = self.aggregate_day_schedule((day_of_week + 1) % 7, group)
        todays_zone_timing = today_schedule[zone_type]
        tomorrows_zone_timing = tomorrow_schedule[zone_type]
        for t in todays_zone_timing:
            if t > hour:
                return now.replace(hour=t, minute=0, second=0, microsecond=0)
        return (now + timedelta(hours=24)).replace(hour=tomorrows_zone_timing[0], minute=0, second=0, microsecond=0).astimezone(pytz.utc)

    def get_next_zone_type_and_time(self, group: str) -> Tuple[ElectricityStateLog.STATE, datetime]:
        zones = dict(ON="yes", OFF="no", UNKNOWN="maybe")
        current_state = self.get_state(group)
        del zones[current_state]
        next_datetime = None
        next_zone_type = None
        for zone in zones.values():
            result = self._next_zone_datetime_by_type(group, zone)
            if not next_datetime or result < next_datetime:
                next_datetime = result
                next_zone_type = zone
        return (next_zone_type, next_datetime)

    def next_black_zone_datetime(self, group: str) -> datetime:
        return self._next_zone_datetime_by_type(group, "no")
    
    def next_gray_zone_datetime(self, group: str) -> datetime:
        return self._next_zone_datetime_by_type(group, "maybe")

    def next_white_zone_datetime(self, group: str) -> datetime:
        return self._next_zone_datetime_by_type(group, "yes")

    def timedelta_to_next_recovery(self, group: str) -> timedelta:
        next_recovery = self.next_white_zone_datetime(group)
        return next_recovery - datetime.now(pytz.utc) if next_recovery is not None else None

    def timedelta_to_next_blackout(self, group: str) -> timedelta:
        next_blackout = self.next_black_zone_datetime(group)
        return next_blackout - datetime.now(pytz.utc) if next_blackout is not None else None

    
    def get_state(self, group: str) -> ElectricityStateLog.STATE:
        STATE = ElectricityStateLog.STATE
        now = datetime.now(self.tz)
        weekday = now.weekday()
        schedule = SCHEDULE[group][str(weekday + 1)]
        state_translation = dict(
            yes=STATE.ON, no=STATE.OFF, maybe=STATE.UNKNOWN)
        return state_translation[schedule[str(now.time().hour + 1)]]


if __name__ == "__main__":
    schedule = ScheduleController()
    print(schedule.next_black_zone_datetime(group="1"))
