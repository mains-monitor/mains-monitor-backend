from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
from app.types import StrEnum, auto


class ElectricityStateLog(Model):

    class STATE(StrEnum):
        UNKNOWN = auto()
        OFF = auto()
        ON = auto()

    ITEM_TYPE = "LOG_ITEM"

    type = UnicodeAttribute(
        hash_key=True, default_for_new=ITEM_TYPE, null=False)
    created = UTCDateTimeAttribute(
        range_key=True, default_for_new=datetime.now, null=False)
    updated = UTCDateTimeAttribute(null=False, default_for_new=datetime.now)
    state = UnicodeAttribute(null=False)
    group = UnicodeAttribute()

    class Meta:
        table_name = "el-st-bot.ElectricityStateLog"
        region = 'eu-west-1'
