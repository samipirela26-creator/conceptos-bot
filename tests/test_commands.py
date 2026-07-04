import pytest
from unittest.mock import AsyncMock, MagicMock

from src.bot.commands import (
    menu_command, menu_callback, favoritos_command, historial_command, favorito_callback,
)
from src.bot import texts
from src.db import DBClient


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


def _context_con_db(db):
    context = MagicMock()
    context.bot_data = {"db": db}
    return context


@pytest.mark.asyncio
async def test_favoritos_command_sin_favoritos():
    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()
    await favoritos_command(update, _context_con_db(DBClient(":memory:")))
    update.message.reply_text.assert_awaited_once()
    assert "no tiene" in update.message.reply_text.call_args.args[0].lower()


@pytest.mark.asyncio
async def test_favoritos_command_con_favoritos():
    db = DBClient(":memory:")
    db.agregar_favorito(1, "casa")
    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()
    await favoritos_command(update, _context_con_db(db))
    mensaje = update.message.reply_text.call_args.args[0]
    assert "casa" in mensaje


@pytest.mark.asyncio
async def test_historial_command_vacio():
    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()
    await historial_command(update, _context_con_db(DBClient(":memory:")))
    assert "no hemos" in update.message.reply_text.call_args.args[0].lower()


@pytest.mark.asyncio
async def test_favorito_callback_agregar():
    db = DBClient(":memory:")
    update = MagicMock()
    update.effective_user.id = 1
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_fav:add:casa"
    update.callback_query.edit_message_reply_markup = AsyncMock()
    update.callback_query.message.reply_text = AsyncMock()
    await favorito_callback(update, _context_con_db(db))
    assert db.es_favorito(1, "casa") is True
    update.callback_query.message.reply_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_favorito_callback_quitar():
    db = DBClient(":memory:")
    db.agregar_favorito(1, "casa")
    update = MagicMock()
    update.effective_user.id = 1
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_fav:quitar:casa"
    update.callback_query.edit_message_text = AsyncMock()
    await favorito_callback(update, _context_con_db(db))
    assert db.es_favorito(1, "casa") is False
    update.callback_query.edit_message_text.assert_awaited_once()
