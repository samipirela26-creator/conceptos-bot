import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot import texts
from src.bot.handlers import handle_message, inline_query_handler, buscar_palabra_del_dia
from src.db import DBClient

RESULTADO_RAE_CASA = {
    "palabra": "casa",
    "etimologia": None,
    "acepciones": [{"texto": "Edificio para habitar", "etiqueta": "f.", "ejemplos": [], "sinonimos": []}],
}


@pytest.mark.asyncio
async def test_inline_query_vacia_no_responde():
    update = MagicMock()
    update.inline_query.query = "   "
    update.inline_query.answer = AsyncMock()
    await inline_query_handler(update, MagicMock())
    update.inline_query.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_inline_query_encontrada_responde_con_resultado():
    update = MagicMock()
    update.inline_query.query = "casa"
    update.inline_query.answer = AsyncMock()
    with patch("src.bot.handlers.buscar_rae", return_value=RESULTADO_RAE_CASA), \
         patch("src.bot.handlers.buscar_wikcionario", return_value=None):
        await inline_query_handler(update, MagicMock())
    update.inline_query.answer.assert_awaited_once()
    resultados = update.inline_query.answer.call_args.args[0]
    assert len(resultados) == 1
    assert "casa" in resultados[0].id


@pytest.mark.asyncio
async def test_inline_query_no_encontrada_no_responde():
    update = MagicMock()
    update.inline_query.query = "asdfqwerty123"
    update.inline_query.answer = AsyncMock()
    with patch("src.bot.handlers.buscar_rae", return_value=None), \
         patch("src.bot.handlers.buscar_wikcionario", return_value=None):
        await inline_query_handler(update, MagicMock())
    update.inline_query.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_message_registra_historial_y_ofrece_favorito():
    db = DBClient(":memory:")
    update = MagicMock()
    update.effective_user.id = 1
    update.message.text = "casa"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.bot_data = {"allowed_user_ids": [], "db": db}

    with patch("src.bot.handlers.buscar_rae", return_value=RESULTADO_RAE_CASA), \
         patch("src.bot.handlers.buscar_wikcionario", return_value=None):
        await handle_message(update, context)

    assert db.listar_historial(1) == ["casa"]
    ultima_llamada = update.message.reply_text.call_args
    assert ultima_llamada.kwargs["reply_markup"] is not None


@pytest.mark.asyncio
async def test_handle_message_no_ofrece_favorito_si_ya_lo_es():
    db = DBClient(":memory:")
    db.agregar_favorito(1, "casa")
    update = MagicMock()
    update.effective_user.id = 1
    update.message.text = "casa"
    update.message.reply_text = AsyncMock()
    context = MagicMock()
    context.bot_data = {"allowed_user_ids": [], "db": db}

    with patch("src.bot.handlers.buscar_rae", return_value=RESULTADO_RAE_CASA), \
         patch("src.bot.handlers.buscar_wikcionario", return_value=None):
        await handle_message(update, context)

    ultima_llamada = update.message.reply_text.call_args
    assert ultima_llamada.kwargs["reply_markup"] is None


def test_buscar_palabra_del_dia_devuelve_concepto_y_resultado():
    with patch("src.bot.handlers.buscar_rae", return_value=RESULTADO_RAE_CASA), \
         patch("src.bot.handlers.buscar_wikcionario", return_value=None):
        encontrada = buscar_palabra_del_dia()
    assert encontrada is not None
    concepto, resultado_rae, resultado_wikcionario = encontrada
    assert concepto in texts.PALABRAS_DEL_DIA
    assert resultado_rae == RESULTADO_RAE_CASA


def test_buscar_palabra_del_dia_ninguna_encontrada_devuelve_none():
    with patch("src.bot.handlers.buscar_rae", return_value=None), \
         patch("src.bot.handlers.buscar_wikcionario", return_value=None):
        assert buscar_palabra_del_dia() is None
