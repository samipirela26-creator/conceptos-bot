"""Entry point del bot de Telegram 'Francis la Búho'."""
import datetime as dt
import sys
from telegram import BotCommand
from telegram.ext import (
    Application, CallbackQueryHandler, CommandHandler, InlineQueryHandler,
    MessageHandler, filters,
)

from src.config import Config
from src.db import DBClient
from src.utils.logger import setup_logger
from src.llm.gemini_client import GeminiClient
from src.bot import texts
from src.bot.formatters import formatear_resultado
from src.bot.commands import (
    start_command, help_command, menu_command, menu_callback,
    favoritos_command, historial_command, favorito_callback,
    palabra_del_dia_command, suscribir_palabra_dia_command, cancelar_palabra_dia_command,
    ahorcado_command, ahorcado_callback,
)
from src.bot.handlers import handle_message, error_handler, inline_query_handler, buscar_palabra_del_dia

logger = None

COMANDOS_PUBLICOS = [
    BotCommand("start", "Presentación del bot"),
    BotCommand("help", "Cómo usar el bot"),
    BotCommand("menu", "Ver menú con botones"),
    BotCommand("favoritos", "Ver sus palabras favoritas"),
    BotCommand("historial", "Ver sus últimas búsquedas"),
    BotCommand("palabradeldia", "Recibir una palabra del día"),
    BotCommand("suscribirpalabradeldia", "Activar el envío diario de la palabra del día"),
    BotCommand("cancelarpalabradeldia", "Desactivar el envío diario de la palabra del día"),
    BotCommand("ahorcado", "Jugar al ahorcado"),
]


async def _post_init(application) -> None:
    await application.bot.set_my_commands(COMANDOS_PUBLICOS)
    logger.info("Menú de comandos (☰) registrado en Telegram.")


async def enviar_palabra_del_dia(context) -> None:
    """Job diario: le manda la palabra del día a cada usuario suscrito
    (opt-in, ver /suscribirpalabradeldia), filtrado por ALLOWED_USER_IDS si
    el bot los tiene configurados."""
    db: DBClient = context.bot_data["db"]
    allowed_user_ids = context.bot_data.get("allowed_user_ids") or []
    suscriptores = db.listar_suscriptores_palabra_dia()
    destinatarios = (
        [uid for uid in suscriptores if uid in allowed_user_ids] if allowed_user_ids else suscriptores
    )
    if not destinatarios:
        return

    encontrada = buscar_palabra_del_dia()
    if encontrada is None:
        logger.warning("No se encontró ninguna palabra del día disponible hoy.")
        return

    concepto, resultado_rae, resultado_wikcionario = encontrada
    mensaje = formatear_resultado(concepto, resultado_rae, resultado_wikcionario)
    texto = f"{texts.PALABRA_DEL_DIA_INTRO}\n\n{mensaje}"

    for user_id in destinatarios:
        try:
            await context.bot.send_message(chat_id=user_id, text=texto, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"No se pudo enviar la palabra del día a {user_id}: {e}")


def main():
    global logger
    try:
        print("Cargando configuración...")
        config = Config()

        logger = setup_logger(config)
        logger.info("=" * 50)
        logger.info("Iniciando bot de conceptos (Francis la Búho)")
        logger.info("=" * 50)

        llm_client = GeminiClient(api_key=config.gemini_api_key, model=config.gemini_model)
        db = DBClient(config.db_path)

        application = Application.builder().token(config.telegram_bot_token).post_init(_post_init).build()
        application.bot_data["llm_client"] = llm_client
        application.bot_data["allowed_user_ids"] = config.allowed_user_ids
        application.bot_data["db"] = db

        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("menu", menu_command))
        application.add_handler(CommandHandler("favoritos", favoritos_command))
        application.add_handler(CommandHandler("historial", historial_command))
        application.add_handler(CommandHandler("palabradeldia", palabra_del_dia_command))
        application.add_handler(CommandHandler("suscribirpalabradeldia", suscribir_palabra_dia_command))
        application.add_handler(CommandHandler("cancelarpalabradeldia", cancelar_palabra_dia_command))
        application.add_handler(CommandHandler("ahorcado", ahorcado_command))
        application.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^francis_menu:"))
        application.add_handler(CallbackQueryHandler(favorito_callback, pattern=r"^francis_fav:"))
        application.add_handler(CallbackQueryHandler(ahorcado_callback, pattern=r"^francis_ahorcado:"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(InlineQueryHandler(inline_query_handler))
        application.add_error_handler(error_handler)

        if application.job_queue is not None:
            application.job_queue.run_daily(
                enviar_palabra_del_dia,
                time=dt.time(hour=8, minute=0),
                days=(0, 1, 2, 3, 4, 5, 6),
                name="palabra_del_dia",
            )
            logger.info("Job de palabra del día (8:00 AM) programado.")
        else:
            logger.warning(
                "JobQueue no disponible (¿falta instalar python-telegram-bot[job-queue]?). "
                "La palabra del día automática no se activará."
            )

        if config.allowed_user_ids:
            logger.info(f"Acceso restringido a user_ids: {config.allowed_user_ids}")
        else:
            logger.warning("ALLOWED_USER_IDS no configurado: cualquiera puede usar el bot.")

        logger.info("Bot iniciado exitosamente. Escuchando mensajes...")
        application.run_polling(
            poll_interval=2.0,
            timeout=30,
            drop_pending_updates=False,
            bootstrap_retries=-1,
            read_timeout=60,
            connect_timeout=30,
        )

    except ValueError as e:
        print(f"Error de configuración: {e}")
        if logger:
            logger.error(f"Error de configuración: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Error fatal: {e}")
        if logger:
            logger.exception(f"Error fatal al iniciar bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
