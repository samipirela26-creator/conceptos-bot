import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.handlers import inline_query_handler

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
