"""Entry point del bot de Telegram 'Francis la Búho'."""
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
from src.bot.commands import (
    start_command, help_command, menu_command, menu_callback,
    favoritos_command, historial_command, favorito_callback,
)
from src.bot.handlers import handle_message, error_handler, inline_query_handler

logger = None

COMANDOS_PUBLICOS = [
    BotCommand("start", "Presentación del bot"),
    BotCommand("help", "Cómo usar el bot"),
    BotCommand("menu", "Ver menú con botones"),
    BotCommand("favoritos", "Ver sus palabras favoritas"),
    BotCommand("historial", "Ver sus últimas búsquedas"),
]


async def _post_init(application) -> None:
    await application.bot.set_my_commands(COMANDOS_PUBLICOS)
    logger.info("Menú de comandos (☰) registrado en Telegram.")


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
        application.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^francis_menu:"))
        application.add_handler(CallbackQueryHandler(favorito_callback, pattern=r"^francis_fav:"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(InlineQueryHandler(inline_query_handler))
        application.add_error_handler(error_handler)

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
