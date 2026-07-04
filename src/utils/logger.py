"""Configuración de logging, mismo patrón que gastos-bot/asistente-bot."""
import logging
import os


def setup_logger(config) -> logging.Logger:
    os.makedirs(config.log_dir, exist_ok=True)
    logger = logging.getLogger('conceptos-bot')
    logger.setLevel(getattr(logging, config.log_level, logging.INFO))

    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    archivo = logging.FileHandler(os.path.join(config.log_dir, 'conceptos-bot.log'))
    archivo.setFormatter(formato)
    logger.addHandler(archivo)

    consola = logging.StreamHandler()
    consola.setFormatter(formato)
    logger.addHandler(consola)

    return logger
