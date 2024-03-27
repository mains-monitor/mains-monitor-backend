from datetime import datetime, timedelta, timezone
from app.models import ElectricityStateLog
from app.logger import logger
from app.types import ElectricityStateUpdate


class ElectricityStatusController:

    @property
    def state(self) -> ElectricityStateLog.STATE:
        try:
            result = ElectricityStateLog.query(
                hash_key=ElectricityStateLog.ITEM_TYPE, limit=1, scan_index_forward=False).next()
        except:
            return ElectricityStateLog.STATE.UNKNOWN
        return result.state if result else ElectricityStateLog.STATE.UNKNOWN

    @property
    def last_report_datetime(self) -> datetime:
        try:
            result = ElectricityStateLog.query(
                hash_key=ElectricityStateLog.ITEM_TYPE, limit=1, scan_index_forward=False).next()
        except:
            return None
        return result.updated if result else None

    @property
    def last_report_timedelta(self) -> timedelta:
        last_report = self.last_report_datetime
        return datetime.now(tz=timezone.utc) - last_report if last_report is not None else None

    def set_electricity_state(self, state_update: ElectricityStateUpdate):
        if state_update.state not in ElectricityStateLog.STATE.values():
            raise ValueError(f"Invalid electricity state value, {state_update.state=}")
        try:
            log_item = ElectricityStateLog.query(
                hash_key=ElectricityStateLog.ITEM_TYPE, limit=1, scan_index_forward=False).next()
        except:
            log_item = None
        if log_item is None or log_item.state != state_update.state:
            new_log_item = ElectricityStateLog()
            new_log_item.state = state_update.state
            new_log_item.group = state_update.group
            new_log_item.save()
            logger.info(f"Created new electricity log item, {state_update.state=} {state_update.group=}")
            return True
        else:
            log_item.update(
                actions=[ElectricityStateLog.updated.set(datetime.now())])
            logger.info(f"Updated existing electricity log item")
            return False

    @property
    def last_switch_datetime(self) -> datetime:
        try:
            result = ElectricityStateLog.query(
                hash_key=ElectricityStateLog.ITEM_TYPE, limit=1, scan_index_forward=False).next()
        except:
            return None
        return result.created if result else None

    @property
    def last_switch_timedelta(self) -> timedelta:
        last_switch = self.last_switch_datetime
        return datetime.now(tz=timezone.utc) - last_switch if last_switch is not None else None

    @property
    def last_switches_timedelta(self) -> timedelta:
        try:
            result = ElectricityStateLog.query(
                hash_key=ElectricityStateLog.ITEM_TYPE, limit=2, scan_index_forward=False)
            switch1 = result.next()
            switch2 = result.next()
        except:
            return None

        return switch1.created - switch2.created if switch1 and switch2 else None
