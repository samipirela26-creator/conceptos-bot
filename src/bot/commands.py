from telegram import Update
from telegram.ext import ContextTypes

from src.bot import texts


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(texts.BIENVENIDA)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(texts.AYUDA)
