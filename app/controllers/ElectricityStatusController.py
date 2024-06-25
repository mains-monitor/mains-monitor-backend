from datetime import datetime, timedelta, timezone
from app.models import ElectricityStateLog
from app.logger import logger
from app.types import ElectricityStateUpdate


class ElectricityStatusController:

    def get_state(self, device_id: str) -> ElectricityStateLog.STATE:
        try:
            result = ElectricityStateLog.query(
                hash_key=device_id,
                limit=1,
                scan_index_forward=False,
            ).next()
        except Exception as _:
            return ElectricityStateLog.STATE.UNKNOWN
        return result.state if result else ElectricityStateLog.STATE.UNKNOWN


    def set_electricity_state(self, state_update: ElectricityStateUpdate):
        if state_update.state not in ElectricityStateLog.STATE.values():
            raise ValueError(f"Invalid electricity state value, {state_update.state=}")
        try:
            log_item = ElectricityStateLog.query(
                hash_key=state_update.devId,
                limit=1,
                scan_index_forward=False,
            ).next()
        except Exception as _:
            log_item = None

        if log_item is None or log_item.state != state_update.state:
            new_log_item = ElectricityStateLog()
            new_log_item.state = state_update.state
            new_log_item.group = state_update.group
            new_log_item.device_id = state_update.devId
            new_log_item.save()
            logger.info(
                "Created new electricity log item, state_update.devId=%s, state_update.state=%s, state_update.group=%s",
                state_update.devId,
                state_update.state,
                state_update.group,
            )
            return True
        else:
            log_item.update(actions=[ElectricityStateLog.updated.set(datetime.now())])
            logger.info("Updated existing electricity log item")
            return False

    def get_last_switch_datetime(self, device_id: str) -> datetime:
        try:
            result = ElectricityStateLog.query(
                hash_key=device_id,
                limit=1,
                scan_index_forward=False,
            ).next()
        except Exception as _:
            return None
        return result.created if result else None

    def get_last_switch_timedelta(self, device_id: str) -> timedelta:
        last_switch = self.get_last_switch_datetime(device_id)
        return (
            datetime.now(tz=timezone.utc) - last_switch
            if last_switch is not None
            else None
        )

    def get_last_switches_timedelta(self, device_id: str) -> timedelta:
        try:
            result = ElectricityStateLog.query(
                hash_key=device_id,
                limit=2,
                scan_index_forward=False,
            )
            switch1 = result.next()
            switch2 = result.next()
        except Exception as _:
            return None

        return switch1.created - switch2.created if switch1 and switch2 else None
