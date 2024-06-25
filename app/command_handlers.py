from telegram import Update
from telegram.ext import ContextTypes
from app.utils.helpers import extract_status_change
from app.utils.decorators import log, chat_tracker
from app.logger import logger
from app.controllers import  NotificationsController

logger.info("Init command handlers")

@chat_tracker
@log("handle_bot_chat")
async def handle_bot_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = extract_status_change(update.my_chat_member)
    if result is None:
        return
    was_member, is_member = result
    chat = update.effective_chat

    notifications = NotificationsController()
    if not was_member and is_member:
        notifications.set_enabled(chat.id, True)
        logger.info("Enabled notifications for %s (%s)", chat.title, chat.id)
    elif was_member and not is_member:
        notifications.set_enabled(chat.id, False)
        logger.info("Disabled notifications for %s (%s)", chat.title, chat.id)

