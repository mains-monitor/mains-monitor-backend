import json
import asyncio
from telegram import Update

from app.bot import bot
from app.logger import logger
import app.command_handlers
from app.controllers import (
    ElectricityStatusController,
    NotificationsController,
    ScheduleController,
)
from app.types import ElectricityStateUpdate, NotificationMessage


async def bot_handler(event, context):
    '''
    Inits Telegram bot and processes the incoming update from Telegram server
    '''
    await bot.initialize()
    update = Update.de_json(json.loads(event["body"]), bot.bot)
    await bot.process_update(update)

    return {"statusCode": 200, "body": "Success"}


def bot_handler_entry(event, context):
    '''
    Entry point for the lambda function that handles the Telegram bot
    '''
    return asyncio.get_event_loop().run_until_complete(bot_handler(event, context))


def electricity_state_change_handler(event, context):
    '''
    Entry point for the lambda function that handles the state change of the electricity
    (messages from Mains Monitor device)
    '''
    electricity = ElectricityStatusController()
    notifications = NotificationsController()
    logger.info(f"Received {event=}")
    state_change_event = json.loads(event["body"])
    state_update = ElectricityStateUpdate(**state_change_event)
    if electricity.set_electricity_state(state_update):
        notifications.enqueue_notifications(state_update)
    return {"statusCode": 200, "body": "Success"}


async def process_messages(event, context):
    notifications = NotificationsController()
    records = event.get("Records")
    logger.info(f"Received {records=}")
    for raw_record in records:
        batch = json.loads(raw_record.get("body"))
        batch = [NotificationMessage(**item) for item in batch]
        await notifications.send_notifications_to_users(batch)


def notifications_handler(event, context):
    '''
    Entry point for the lambda function that is sending Telegram notifications out when the electricity state changes
    '''
    return asyncio.get_event_loop().run_until_complete(process_messages(event, context))


async def error_handler(*args, **kwargs):
    print(f"Error handler {args=} {kwargs=}")


if __name__ == "__main__":
    # schedule = ScheduleController()
    # print(schedule.next_blackout_datetime(group="1"))
    # bot.add_error_handler(error_handler)
    # bot.run_polling()
    # electricity_state_change_handler(
    #     dict(body=json.dumps(dict(state="OFF", group="1"))), None
    # )
    asyncio.get_event_loop().run_until_complete(
        process_messages(
            dict(
                Records=[
                    dict(
                        body=json.dumps(
                            [
                                {
                                    "user_id": "-1001956500775",
                                    "groups": ["1", "2"],
                                    "state_update": {"state": "OFF", "group": "1"},
                                    "schedule_enabled": False
                                }
                            ]
                        )
                    )
                ]
            ),
            None,
        )
    )
    pass