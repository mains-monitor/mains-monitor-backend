import os
from enum import auto
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
from app.types import StrEnum


class ElectricityStateLog(Model):

    class STATE(StrEnum):
        UNKNOWN = auto()
        OFF = auto()
        ON = auto()

    device_id = UnicodeAttribute(hash_key=True, null=False)
    created = UTCDateTimeAttribute(
        range_key=True, default_for_new=datetime.now, null=False)
    updated = UTCDateTimeAttribute(null=False, default_for_new=datetime.now)
    state = UnicodeAttribute(null=False)
    group = UnicodeAttribute()
    

    class Meta:
        table_name = os.getenv("ELECTRICITY_STATE_LOG_TABLE")
        region = os.getenv("AWS_DEFAULT_REGION")
