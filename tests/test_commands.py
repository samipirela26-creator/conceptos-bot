import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.commands import (
    menu_command, menu_callback, favoritos_command, historial_command, favorito_callback,
    palabra_del_dia_command, suscribir_palabra_dia_command, cancelar_palabra_dia_command,
    ahorcado_command, ahorcado_callback, juegos_command, juegos_callback,
)
from src.bot import texts
from src.db import DBClient

RESULTADO_RAE_CASA = {
    "palabra": "casa",
    "etimologia": None,
    "acepciones": [{"texto": "Edificio para habitar", "etiqueta": "f.", "ejemplos": [], "sinonimos": []}],
}


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


@pytest.mark.asyncio
async def test_palabra_del_dia_command_encontrada():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    with patch("src.bot.commands.buscar_palabra_del_dia", return_value=("casa", RESULTADO_RAE_CASA, None)):
        await palabra_del_dia_command(update, MagicMock())
    mensaje = update.message.reply_text.call_args.args[0]
    assert texts.PALABRA_DEL_DIA_INTRO in mensaje
    assert "casa" in mensaje.lower()


@pytest.mark.asyncio
async def test_palabra_del_dia_command_sin_resultado():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    with patch("src.bot.commands.buscar_palabra_del_dia", return_value=None):
        await palabra_del_dia_command(update, MagicMock())
    update.message.reply_text.assert_awaited_once_with(texts.ERROR_SERVICIO)


@pytest.mark.asyncio
async def test_suscribir_palabra_dia_command():
    db = DBClient(":memory:")
    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()
    await suscribir_palabra_dia_command(update, _context_con_db(db))
    assert db.esta_suscrito_palabra_dia(1) is True
    update.message.reply_text.assert_awaited_once_with(texts.PALABRA_DIA_SUSCRITO)


@pytest.mark.asyncio
async def test_cancelar_palabra_dia_command():
    db = DBClient(":memory:")
    db.suscribir_palabra_dia(1)
    update = MagicMock()
    update.effective_user.id = 1
    update.message.reply_text = AsyncMock()
    await cancelar_palabra_dia_command(update, _context_con_db(db))
    assert db.esta_suscrito_palabra_dia(1) is False
    update.message.reply_text.assert_awaited_once_with(texts.PALABRA_DIA_DESUSCRITO)


@pytest.mark.asyncio
async def test_menu_callback_activa_palabra_dia():
    db = DBClient(":memory:")
    update = MagicMock()
    update.effective_user.id = 1
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_menu:palabradia_on"
    update.callback_query.edit_message_reply_markup = AsyncMock()
    update.callback_query.message.reply_text = AsyncMock()
    await menu_callback(update, _context_con_db(db))
    assert db.esta_suscrito_palabra_dia(1) is True
    update.callback_query.message.reply_text.assert_awaited_once_with(texts.PALABRA_DIA_SUSCRITO)


@pytest.mark.asyncio
async def test_menu_callback_desactiva_palabra_dia():
    db = DBClient(":memory:")
    db.suscribir_palabra_dia(1)
    update = MagicMock()
    update.effective_user.id = 1
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_menu:palabradia_off"
    update.callback_query.edit_message_reply_markup = AsyncMock()
    update.callback_query.message.reply_text = AsyncMock()
    await menu_callback(update, _context_con_db(db))
    assert db.esta_suscrito_palabra_dia(1) is False
    update.callback_query.message.reply_text.assert_awaited_once_with(texts.PALABRA_DIA_DESUSCRITO)


def _context_con_user_data(user_data=None):
    context = MagicMock()
    context.user_data = user_data if user_data is not None else {}
    return context


@pytest.mark.asyncio
async def test_ahorcado_command_inicia_partida():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    context = _context_con_user_data()
    await ahorcado_command(update, context)
    update.message.reply_text.assert_awaited_once()
    assert "ahorcado" in context.user_data
    mensaje = update.message.reply_text.call_args.args[0]
    assert texts.AHORCADO_INTRO in mensaje


@pytest.mark.asyncio
async def test_ahorcado_callback_letra_correcta_edita_mensaje():
    context = _context_con_user_data({"ahorcado": {"palabra": "casa", "letras_intentadas": set(), "errores": 0}})
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_ahorcado:letra:C"
    update.callback_query.edit_message_text = AsyncMock()
    await ahorcado_callback(update, context)
    update.callback_query.edit_message_text.assert_awaited_once()
    assert context.user_data["ahorcado"]["letras_intentadas"] == {"C"}


@pytest.mark.asyncio
async def test_ahorcado_callback_pista_usa_rae():
    context = _context_con_user_data({"ahorcado": {"palabra": "casa", "letras_intentadas": set(), "errores": 0}})
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_ahorcado:pista"
    update.callback_query.message.reply_text = AsyncMock()
    with patch("src.bot.commands.obtener_pista", return_value="Edificio para habitar"):
        await ahorcado_callback(update, context)
    update.callback_query.message.reply_text.assert_awaited_once_with("Edificio para habitar")


@pytest.mark.asyncio
async def test_ahorcado_callback_rendirse_revela_palabra():
    context = _context_con_user_data({"ahorcado": {"palabra": "casa", "letras_intentadas": set(), "errores": 0}})
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_ahorcado:rendirse"
    update.callback_query.edit_message_text = AsyncMock()
    await ahorcado_callback(update, context)
    mensaje = update.callback_query.edit_message_text.call_args.args[0]
    assert "casa" in mensaje.lower()
    assert "ahorcado" not in context.user_data


@pytest.mark.asyncio
async def test_juegos_command_muestra_categorias():
    update = MagicMock()
    update.message.reply_text = AsyncMock()
    await juegos_command(update, MagicMock())
    update.message.reply_text.assert_awaited_once()
    _, kwargs = update.message.reply_text.call_args
    assert kwargs["reply_markup"] is not None
    assert texts.JUEGOS_INTRO in update.message.reply_text.call_args.args[0]


@pytest.mark.asyncio
async def test_juegos_callback_elige_categoria_muestra_juegos():
    context = _context_con_user_data()
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_juegos:cat:fe"
    update.callback_query.edit_message_text = AsyncMock()
    await juegos_callback(update, context)
    mensaje, kwargs = update.callback_query.edit_message_text.call_args.args, update.callback_query.edit_message_text.call_args.kwargs
    assert "Fe y reflexión" in mensaje[0]
    assert kwargs["reply_markup"] is not None


@pytest.mark.asyncio
async def test_juegos_callback_inicia_juego():
    context = _context_con_user_data()
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_juegos:juego:fe_gratitud_diaria"
    update.callback_query.edit_message_text = AsyncMock()
    await juegos_callback(update, context)
    update.callback_query.edit_message_text.assert_awaited_once()
    assert "juegos" in context.user_data


@pytest.mark.asyncio
async def test_juegos_callback_siguiente_avanza():
    context = _context_con_user_data()
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_juegos:juego:fe_gratitud_diaria"
    update.callback_query.edit_message_text = AsyncMock()
    await juegos_callback(update, context)

    update.callback_query.data = "francis_juegos:siguiente"
    await juegos_callback(update, context)
    assert update.callback_query.edit_message_text.await_count == 2


@pytest.mark.asyncio
async def test_juegos_callback_salir_termina_juego():
    context = _context_con_user_data()
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_juegos:juego:fe_gratitud_diaria"
    update.callback_query.edit_message_text = AsyncMock()
    await juegos_callback(update, context)

    update.callback_query.data = "francis_juegos:salir"
    await juegos_callback(update, context)
    assert "juegos" not in context.user_data


@pytest.mark.asyncio
async def test_juegos_callback_volver_a_categorias():
    context = _context_con_user_data()
    update = MagicMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "francis_juegos:categorias"
    update.callback_query.edit_message_text = AsyncMock()
    await juegos_callback(update, context)
    mensaje = update.callback_query.edit_message_text.call_args.args[0]
    assert texts.JUEGOS_INTRO in mensaje
