"""Handlers de Telegram. El flujo es siempre: 1) entender qué palabra pide
el usuario (heurística, y si hace falta, Gemini SOLO para esto) 2) consultar
RAE + Wikcionario (fuentes reales, nunca generadas) 3) formatear y responder."""
import logging
import random

from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,
    InputTextMessageContent, Update,
)
from telegram.ext import ContextTypes

from src.bot import texts
from src.bot.formatters import formatear_resultado
from src.utils.concept_extractor import extraer_heuristico
from src.services.rae import buscar_rae
from src.services.wikcionario import buscar_wikcionario

logger = logging.getLogger('conceptos-bot')


def _acceso_permitido(user_id: int, allowed_user_ids: list[int]) -> bool:
    return not allowed_user_ids or user_id in allowed_user_ids


def _buscar_concepto(concepto: str) -> tuple[dict | None, dict | None, bool]:
    """Consulta RAE + Wikcionario para un concepto ya extraído. Devuelve
    (resultado_rae, resultado_wikcionario, hubo_error_servicio)."""
    resultado_rae = None
    resultado_wikcionario = None
    hubo_error_servicio = False

    try:
        resultado_rae = buscar_rae(concepto)
    except RuntimeError as e:
        logger.error(f"Error consultando RAE para '{concepto}': {e}")
        hubo_error_servicio = True

    try:
        resultado_wikcionario = buscar_wikcionario(concepto)
    except RuntimeError as e:
        logger.error(f"Error consultando Wikcionario para '{concepto}': {e}")
        hubo_error_servicio = True

    return resultado_rae, resultado_wikcionario, hubo_error_servicio


def buscar_palabra_del_dia() -> tuple[str, dict | None, dict | None] | None:
    """Elige una palabra al azar de texts.PALABRAS_DEL_DIA y la busca en
    RAE/Wikcionario, reintentando con otra palabra si alguna no aparece en
    ninguna fuente. Devuelve None si ninguna de las candidatas dio resultado."""
    candidatas = random.sample(texts.PALABRAS_DEL_DIA, k=len(texts.PALABRAS_DEL_DIA))
    for concepto in candidatas:
        resultado_rae, resultado_wikcionario, _ = _buscar_concepto(concepto)
        if resultado_rae or resultado_wikcionario:
            return concepto, resultado_rae, resultado_wikcionario
    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    allowed_user_ids = context.bot_data.get("allowed_user_ids") or []
    if not _acceso_permitido(update.effective_user.id, allowed_user_ids):
        return

    db = context.bot_data.get("db")

    mensaje = update.message.text
    concepto = extraer_heuristico(mensaje)

    if concepto is None:
        llm_client = context.bot_data.get("llm_client")
        try:
            concepto = llm_client.extraer_concepto(mensaje)
        except Exception as e:
            logger.warning(f"Gemini falló al extraer el concepto: {e}")
            concepto = None

    if concepto is None:
        await update.message.reply_text(texts.charla())
        return

    await update.message.reply_text(texts.trabajando())

    resultado_rae, resultado_wikcionario, hubo_error_servicio = _buscar_concepto(concepto)

    if not resultado_rae and not resultado_wikcionario:
        if hubo_error_servicio:
            await update.message.reply_text(texts.ERROR_SERVICIO)
        else:
            await update.message.reply_text(texts.no_encontrado(concepto))
        return

    user_id = update.effective_user.id
    if db is not None:
        db.registrar_historial(user_id, concepto)
        ya_es_favorito = db.es_favorito(user_id, concepto)
    else:
        ya_es_favorito = False

    mensaje_final = formatear_resultado(concepto, resultado_rae, resultado_wikcionario)
    teclado = None
    # callback_data de Telegram tiene un límite de 64 bytes; "francis_fav:add:"
    # ya ocupa 17, así que se omite el botón para conceptos inusualmente largos.
    if db is not None and not ya_es_favorito and len(concepto.encode("utf-8")) <= 40:
        teclado = InlineKeyboardMarkup([[
            InlineKeyboardButton("⭐ Guardar en favoritos", callback_data=f"francis_fav:add:{concepto}"),
        ]])
    await update.message.reply_text(mensaje_final, parse_mode="Markdown", reply_markup=teclado)


async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Permite consultar '@<bot> palabra' desde cualquier chat. No usa Gemini
    (para responder rápido dentro del tiempo límite de una inline query de
    Telegram) -- si la heurística no reconoce un patrón, se usa el texto tal
    cual como concepto."""
    consulta = (update.inline_query.query or "").strip()
    if not consulta:
        return

    concepto = extraer_heuristico(consulta) or consulta
    resultado_rae, resultado_wikcionario, hubo_error_servicio = _buscar_concepto(concepto)

    if not resultado_rae and not resultado_wikcionario:
        return

    mensaje = formatear_resultado(concepto, resultado_rae, resultado_wikcionario)
    resultado = InlineQueryResultArticle(
        id=concepto,
        title=f'Definición de "{concepto}"',
        description="RAE + Wikcionario, servido por Francis la Búho 🦉",
        input_message_content=InputTextMessageContent(mensaje, parse_mode="Markdown"),
    )
    await update.inline_query.answer([resultado], cache_time=300)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception(f"Error no manejado: {context.error}")
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(texts.ERROR_SERVICIO)
        except Exception:
            pass
