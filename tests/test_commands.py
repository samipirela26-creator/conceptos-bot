import pytest
from unittest.mock import AsyncMock, MagicMock

from src.bot.commands import menu_command, menu_callback
from src.bot import texts


@pytest.mark.asyncio
async def test_menu_command_envia_teclado():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    await menu_command(update, MagicMock())
    update.message.reply_text.assert_awaited_once()
    _, kwargs = update.message.reply_text.call_args
    assert "reply_markup" in kwargs


@pytest.mark.asyncio
async def test_menu_callback_ayuda():
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_menu:ayuda"
    update.callback_query.message.reply_text = AsyncMock()
    await menu_callback(update, MagicMock())
    update.callback_query.message.reply_text.assert_awaited_once_with(texts.AYUDA)


@pytest.mark.asyncio
async def test_menu_callback_acerca():
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_menu:acerca"
    update.callback_query.message.reply_text = AsyncMock()
    await menu_callback(update, MagicMock())
    update.callback_query.message.reply_text.assert_awaited_once_with(texts.ACERCA_DE)
