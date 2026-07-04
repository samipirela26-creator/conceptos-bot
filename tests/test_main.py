import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.main import enviar_palabra_del_dia
from src.db import DBClient

RESULTADO_RAE_CASA = {
    "palabra": "casa",
    "etimologia": None,
    "acepciones": [{"texto": "Edificio para habitar", "etiqueta": "f.", "ejemplos": [], "sinonimos": []}],
}


@pytest.mark.asyncio
async def test_enviar_palabra_del_dia_usa_allowed_user_ids_si_estan_configurados():
    db = DBClient(":memory:")
    db.registrar_usuario(999)
    context = MagicMock()
    context.bot_data = {"db": db, "allowed_user_ids": [1, 2]}
    context.bot.send_message = AsyncMock()

    with patch("src.main.buscar_palabra_del_dia", return_value=("casa", RESULTADO_RAE_CASA, None)):
        await enviar_palabra_del_dia(context)

    destinatarios = {c.kwargs["chat_id"] for c in context.bot.send_message.await_args_list}
    assert destinatarios == {1, 2}


@pytest.mark.asyncio
async def test_enviar_palabra_del_dia_usa_usuarios_registrados_si_no_hay_allowed_ids():
    db = DBClient(":memory:")
    db.registrar_usuario(42)
    context = MagicMock()
    context.bot_data = {"db": db, "allowed_user_ids": []}
    context.bot.send_message = AsyncMock()

    with patch("src.main.buscar_palabra_del_dia", return_value=("casa", RESULTADO_RAE_CASA, None)):
        await enviar_palabra_del_dia(context)

    context.bot.send_message.assert_awaited_once()
    assert context.bot.send_message.call_args.kwargs["chat_id"] == 42


@pytest.mark.asyncio
async def test_enviar_palabra_del_dia_sin_destinatarios_no_busca_ni_envia():
    db = DBClient(":memory:")
    context = MagicMock()
    context.bot_data = {"db": db, "allowed_user_ids": []}
    context.bot.send_message = AsyncMock()

    with patch("src.main.buscar_palabra_del_dia") as mock_buscar:
        await enviar_palabra_del_dia(context)

    mock_buscar.assert_not_called()
    context.bot.send_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_enviar_palabra_del_dia_nada_encontrado_no_envia():
    db = DBClient(":memory:")
    context = MagicMock()
    context.bot_data = {"db": db, "allowed_user_ids": [1]}
    context.bot.send_message = AsyncMock()

    with patch("src.main.buscar_palabra_del_dia", return_value=None), \
         patch("src.main.logger", MagicMock()):
        await enviar_palabra_del_dia(context)

    context.bot.send_message.assert_not_awaited()
