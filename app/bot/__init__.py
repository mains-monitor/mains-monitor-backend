import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

load_dotenv()
bot = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

__all__=["bot"]