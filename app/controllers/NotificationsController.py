import os
import json
import random
import dataclasses
from typing import List, Dict
import boto3
from telegram import Bot
from app.bot import bot
from app.models import Notifications
from app.types import ElectricityStateUpdate, NotificationMessage
from app.logger import logger
from app.controllers import ScheduleController, ElectricityStatusController
from app.jinja import jinja

MAX_BATCH_SIZE = 20

sqs = boto3.client("sqs")


class NotificationsController:
    def __init__(self) -> None:
        self.queue_url = os.getenv("QUEUE_URL")

    def enabled(self, user_id) -> bool:
        try:
            setting = Notifications.get(hash_key=1, range_key=user_id)
            return setting is not None
        except:
            return False

    def set_enabled(self, user_id, value):
        user_id = str(user_id)
        if value:
            notification = Notifications(hash_key=1, range_key=user_id)
            notification.groups = []
            notification.save()
        else:
            notification = Notifications.get(hash_key=1, range_key=user_id)
            notification.delete(condition=(Notifications.user_id == user_id))

    def enqueue_notifications(self, state_update: ElectricityStateUpdate):
        subscriptions = Notifications.query(hash_key=1)
        batch = []
        effective_delay = 0
        delay_increment = 10
        while True:
            try:
                for _ in range(MAX_BATCH_SIZE):
                    subscription = next(subscriptions)
                    data = dict(
                        user_id=subscription.user_id,
                        groups=subscription.groups,
                        state_update=dataclasses.asdict(state_update),
                        schedule_enabled=subscription.schedule_enabled
                    )
                    batch.append(
                        data
                    ) if state_update.group in subscription.groups else None
                if batch:
                    self._send_batch(batch, effective_delay)
                    effective_delay += delay_increment
                    batch = []
            except:
                self._send_batch(batch, effective_delay) if batch else None
                break

    def _send_batch(self, batch: List[Dict[str, any]], delay: int):
        logger.info(f"Sending message to SQS, {batch=}")
        sqs.send_message(
            QueueUrl=self.queue_url, MessageBody=json.dumps(batch), DelaySeconds=delay
        )

    async def send_notifications_to_users(self, batch: List[NotificationMessage]):
        if len(batch) > MAX_BATCH_SIZE:
            raise RuntimeError(f"Too many notifications for a single batch")
        sender: Bot = bot.bot
        logger.info(f"Sending notifications {batch=}")

        schedule = ScheduleController()
        electricity_status = ElectricityStatusController()

        electricity_emoji = ["💡", "🌝", "🙌", "😃", "🥳"]
        blackout_emoji = ["🕯", "😢", "😭", "😩", "😫", "😒", "🌚", "😑"]

        for message in batch:
            groups_state = dict()
            for group in message.groups:
                next_zone, next_zone_datetime = schedule.get_next_zone_type_and_time(
                    group
                )
                group_state = dict(
                    state_by_schedule=schedule.get_state(group),
                    next_zone=next_zone,
                    next_zone_datetime=next_zone_datetime,
                )
                groups_state[group] = group_state
            args = dict(
                message=message,
                state=message.state_update.get("state", None),
                on_emoji=random.choice(electricity_emoji),
                off_emoji=random.choice(blackout_emoji),
                groups=message.groups,
                groups_state=groups_state,
                last_switches_timedelta=electricity_status.last_switches_timedelta,
            )
            logger.info(args)
            template = jinja.get_template("chat_notification_msg.md")
            rendered = template.render(**args)
            #print(rendered)
            await sender.send_message(
                int(message.user_id), text=rendered, parse_mode="markdownV2"
            )
