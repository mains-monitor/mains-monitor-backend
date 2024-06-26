import os
from pynamodb.models import Model
from pynamodb.attributes import NumberAttribute, UnicodeAttribute, ListAttribute, BooleanAttribute


class Notifications(Model):

    enabled = NumberAttribute(hash_key=True, default_for_new=1, null=False)
    user_id = UnicodeAttribute(range_key=True, null=False)
    groups = ListAttribute(null=False, default=list)
    schedule_enabled = BooleanAttribute(default=False, default_for_new=False, null=False)

    class Meta:
        table_name = os.getenv("NOTIFICATION_SETTINGS_TABLE")
        region = os.getenv("AWS_DEFAULT_REGION")
