"""Motor genérico de juegos de conversación (100 juegos en 10 categorías,
catálogo de contenido en juegos_data.py). El estado de la partida vive en
context.user_data (en memoria, por usuario), igual que el ahorcado -- es una
sesión de juego, no un dato de perfil que valga la pena persistir en SQLite."""
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot import texts
from src.bot.juegos_data import CATEGORIAS, JUEGOS

_CLAVE_ESTADO = "juegos"


def teclado_categorias() -> InlineKeyboardMarkup:
    filas = [
        [InlineKeyboardButton(categoria["nombre"], callback_data=f"francis_juegos:cat:{categoria['id']}")]
        for categoria in CATEGORIAS
    ]
    return InlineKeyboardMarkup(filas)


def nombre_categoria(categoria_id: str) -> str | None:
    for categoria in CATEGORIAS:
        if categoria["id"] == categoria_id:
            return categoria["nombre"]
    return None


def _juegos_de_categoria(categoria_id: str) -> list[tuple[str, dict]]:
    return [
        (juego_id, juego) for juego_id, juego in JUEGOS.items()
        if juego["categoria"] == categoria_id
    ]


def teclado_juegos_de_categoria(categoria_id: str) -> InlineKeyboardMarkup | None:
    juegos = _juegos_de_categoria(categoria_id)
    if not juegos:
        return None
    filas = [
        [InlineKeyboardButton(juego["titulo"], callback_data=f"francis_juegos:juego:{juego_id}")]
        for juego_id, juego in juegos
    ]
    filas.append([InlineKeyboardButton("⬅️ Categorías", callback_data="francis_juegos:categorias")])
    return InlineKeyboardMarkup(filas)


def _teclado_en_juego() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("➡️ Siguiente", callback_data="francis_juegos:siguiente"),
        InlineKeyboardButton("🚪 Salir", callback_data="francis_juegos:salir"),
    ]])


def iniciar_juego(user_data: dict, juego_id: str) -> tuple[str, InlineKeyboardMarkup] | None:
    juego = JUEGOS.get(juego_id)
    if juego is None:
        return None
    pendientes = list(range(len(juego["prompts"])))
    random.shuffle(pendientes)
    primero = pendientes.pop()
    user_data[_CLAVE_ESTADO] = {"juego_id": juego_id, "pendientes": pendientes}
    mensaje = f"🦉 {juego['titulo']}\n\n{juego['prompts'][primero]}"
    return mensaje, _teclado_en_juego()


def siguiente_prompt(user_data: dict) -> tuple[str, InlineKeyboardMarkup | None, bool]:
    """Devuelve (mensaje, teclado_o_None, terminado)."""
    estado = user_data.get(_CLAVE_ESTADO)
    if estado is None:
        return texts.JUEGOS_SIN_JUEGO, None, True

    if not estado["pendientes"]:
        del user_data[_CLAVE_ESTADO]
        return texts.juegos_fin(), None, True

    juego = JUEGOS[estado["juego_id"]]
    indice = estado["pendientes"].pop()
    mensaje = f"🦉 {juego['titulo']}\n\n{juego['prompts'][indice]}"
    return mensaje, _teclado_en_juego(), False


def salir_juego(user_data: dict) -> str:
    estado = user_data.pop(_CLAVE_ESTADO, None)
    if estado is None:
        return texts.JUEGOS_SIN_JUEGO
    juego = JUEGOS[estado["juego_id"]]
    return texts.juegos_salida(juego["titulo"])


def juego_actual(user_data: dict) -> str | None:
    estado = user_data.get(_CLAVE_ESTADO)
    return estado["juego_id"] if estado else None
