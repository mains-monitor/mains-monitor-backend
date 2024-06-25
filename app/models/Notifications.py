import os
from pynamodb.models import Model
from pynamodb.attributes import NumberAttribute, UnicodeAttribute, ListAttribute, BooleanAttribute


class Notifications(Model):

    device_id = UnicodeAttribute(hash_key=True, null=False, default_for_new="unknown")
    chat_id = UnicodeAttribute(range_key=True, null=False)
    enabled = NumberAttribute(default_for_new=1, null=False)
    groups = ListAttribute(null=False, default=list)
    schedule_enabled = BooleanAttribute(default=False, default_for_new=False, null=False)
    role = UnicodeAttribute(null=False, default_for_new="")
    template = UnicodeAttribute(null=False, default_for_new="")

    class Meta:
        table_name = os.getenv("NOTIFICATION_SETTINGS_TABLE")
        region = os.getenv("AWS_DEFAULT_REGION")
