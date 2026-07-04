from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot import texts


def _menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Cómo consultarme", callback_data="francis_menu:ayuda")],
        [InlineKeyboardButton("🦉 Acerca de Francis", callback_data="francis_menu:acerca")],
    ])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(texts.BIENVENIDA)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(texts.AYUDA)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🦉 ¿En qué puedo servirle?", reply_markup=_menu_keyboard())


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    accion = (query.data or "").split(":", 1)[-1]
    if accion == "ayuda":
        await query.message.reply_text(texts.AYUDA)
    elif accion == "acerca":
        await query.message.reply_text(texts.ACERCA_DE)
