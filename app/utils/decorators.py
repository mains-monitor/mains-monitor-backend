import logging
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ChatMemberHandler
from telegram.constants import ChatAction
from app.bot import bot


def slash_command_handler(command: str):
    def decorator(func):
        handler = CommandHandler(command, func)
        bot.add_handler(handler)
        return func
    return decorator


def text_command_handler(text_command: str):
    def decorator(func):
        handler = MessageHandler(
            filters=(filters.TEXT & ~filters.COMMAND & filters.Text(text_command)), callback=func)
        bot.add_handler(handler)
        return func
    return decorator


def log(cat: str):
    def decorator(func):
        def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):
            logger = logging.getLogger(cat)
            chat_id = update.effective_chat.id
            user_id = update.effective_user.id
            user_name = update._effective_user.username
            logger.info(f"{chat_id=}, {user_id=}, {user_name=}")
            return func(update, context)
        return decorated
    return decorator


def simulate_typing(func):
    async def decorated(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_chat.send_chat_action(action=ChatAction.TYPING)
        return await func(update, context)
    return decorated


def query_handler(func):
    handler = CallbackQueryHandler(func)
    bot.add_handler(handler)
    return func


def chat_tracker(func):
    handler = ChatMemberHandler(func, ChatMemberHandler.MY_CHAT_MEMBER)
    bot.add_handler(handler)
    return func