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

    def set_enabled(self, chat_id, value):
        chat_id = str(chat_id)
        target_value = 1 if value else 0
        item_updated = False
        for item in Notifications.scan(Notifications.chat_id == chat_id):
            item.enabled = target_value
            item.save()
            item_updated = True
        if not item_updated:
            item = Notifications(chat_id=chat_id, enabled=target_value)
            item.save()

    def enqueue_notifications(self, state_update: ElectricityStateUpdate):
        subscriptions = Notifications.query(hash_key=state_update.devId)
        batch = []
        effective_delay = 0
        delay_increment = 10
        while True:
            try:
                for _ in range(MAX_BATCH_SIZE):
                    subscription = next(subscriptions)
                    if not subscription.enabled:
                        logger.warning(
                            "Subscription for chat %s is disabled. State update from %s will not be sent",
                            subscription.chat_id,
                            state_update.devId,
                        )
                        continue
                    notification_message = NotificationMessage(
                        chat_id=subscription.chat_id,
                        groups=subscription.groups,
                        state_update=state_update,
                        schedule_enabled=subscription.schedule_enabled,
                    )
                    data = dataclasses.asdict(notification_message)
                    if state_update.group in subscription.groups:
                        batch.append(data)
                    else:
                        logger.warning(
                            "Group %s is not in the list of groups %s. State update from %s will not be sent to chat %s",
                            state_update.group,
                            subscription.groups,
                            state_update.devId,
                            subscription.chat_id,
                        )
                if batch:
                    self._send_batch(batch, effective_delay)
                    effective_delay += delay_increment
                    batch = []
            except Exception as _:
                if batch:
                    self._send_batch(batch, effective_delay)
                break

    def _send_batch(self, batch: List[Dict[str, any]], delay: int):
        logger.info("Sending message to SQS, %s", batch)
        sqs.send_message(
            QueueUrl=self.queue_url, MessageBody=json.dumps(batch), DelaySeconds=delay
        )

    async def send_notifications_to_users(self, batch: List[NotificationMessage]):
        if len(batch) > MAX_BATCH_SIZE:
            raise RuntimeError("Too many notifications for a single batch")
        sender: Bot = bot.bot
        logger.info("Sending notifications via Telegram %s", batch)

        schedule = ScheduleController()
        electricity_status = ElectricityStatusController()

        electricity_emoji = ["💡", "🌝", "🙌", "😃", "🥳"]
        blackout_emoji = ["🕯", "😢", "😭", "😩", "😫", "😒", "🌚", "😑"]

        for message in batch:
            groups_state = dict()
            for group in message.groups:
                forecast = schedule.get_next_zones_forecast(group)
                current_state, till = schedule.get_state(group)
                group_state = dict(
                    current_state=current_state,
                    till=till,
                    forecast=forecast,
                )
                groups_state[group] = group_state
            args = dict(
                message=message,
                state=message.state_update.state,
                on_emoji=random.choice(electricity_emoji),
                off_emoji=random.choice(blackout_emoji),
                groups=message.groups,
                groups_state=groups_state,
                last_switches_timedelta=electricity_status.get_last_switches_timedelta(message.state_update.devId),
            )
            logger.info(args)
            template = jinja.get_template("chat_notification_msg.md")
            rendered = template.render(**args)

            await sender.send_message(
                int(message.chat_id), text=rendered, parse_mode="markdownV2"
            )
