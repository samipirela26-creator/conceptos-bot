"""Juego del ahorcado. El estado de cada partida vive en context.user_data
(en memoria, por usuario) -- no es un dato que valga la pena persistir en
SQLite como favoritos/historial. La pista, cuando se pide, sigue la misma
regla del resto del bot: sale tal cual de RAE/Wikcionario, nunca inventada."""
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot import texts

ALFABETO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
MAX_ERRORES = 6
_CLAVE_ESTADO = "ahorcado"

_MAPA_ACENTOS = str.maketrans("ÁÉÍÓÚÜáéíóúü", "AEIOUUaeiouu")


def _normalizar(letra: str) -> str:
    return letra.translate(_MAPA_ACENTOS).upper()


def _palabra_mostrada(palabra: str, letras_intentadas: set[str]) -> str:
    return " ".join(
        letra if _normalizar(letra) in letras_intentadas else "_"
        for letra in palabra
    )


def _teclado(letras_intentadas: set[str]) -> InlineKeyboardMarkup:
    disponibles = [letra for letra in ALFABETO if letra not in letras_intentadas]
    filas = [
        [
            InlineKeyboardButton(letra, callback_data=f"francis_ahorcado:letra:{letra}")
            for letra in disponibles[i:i + 7]
        ]
        for i in range(0, len(disponibles), 7)
    ]
    filas.append([
        InlineKeyboardButton("💡 Pista", callback_data="francis_ahorcado:pista"),
        InlineKeyboardButton("🏳️ Rendirse", callback_data="francis_ahorcado:rendirse"),
    ])
    return InlineKeyboardMarkup(filas)


def _mensaje_estado(juego: dict) -> str:
    mostrado = _palabra_mostrada(juego["palabra"], juego["letras_intentadas"])
    letras_usadas = ", ".join(sorted(juego["letras_intentadas"])) or "ninguna"
    return (
        f"🦉 {mostrado}\n\n"
        f"Errores: {juego['errores']}/{MAX_ERRORES}\n"
        f"Letras usadas: {letras_usadas}"
    )


def _gano(juego: dict) -> bool:
    return all(_normalizar(letra) in juego["letras_intentadas"] for letra in juego["palabra"])


def iniciar_juego(user_data: dict) -> tuple[str, InlineKeyboardMarkup]:
    palabra = random.choice(texts.PALABRAS_AHORCADO)
    juego = {"palabra": palabra, "letras_intentadas": set(), "errores": 0}
    user_data[_CLAVE_ESTADO] = juego
    mensaje = f"{texts.AHORCADO_INTRO}\n\n{_mensaje_estado(juego)}"
    return mensaje, _teclado(juego["letras_intentadas"])


def procesar_letra(user_data: dict, letra: str) -> tuple[str, InlineKeyboardMarkup | None, bool]:
    """Devuelve (mensaje, teclado_o_None, terminado)."""
    juego = user_data.get(_CLAVE_ESTADO)
    if juego is None:
        return texts.AHORCADO_SIN_JUEGO, None, True

    if letra not in juego["letras_intentadas"]:
        juego["letras_intentadas"].add(letra)
        if letra not in {_normalizar(c) for c in juego["palabra"]}:
            juego["errores"] += 1

    if _gano(juego):
        mensaje = f"{_mensaje_estado(juego)}\n\n{texts.ahorcado_ganado()}"
        del user_data[_CLAVE_ESTADO]
        return mensaje, None, True

    if juego["errores"] >= MAX_ERRORES:
        mensaje = f"{_mensaje_estado(juego)}\n\n{texts.ahorcado_perdido(juego['palabra'])}"
        del user_data[_CLAVE_ESTADO]
        return mensaje, None, True

    return _mensaje_estado(juego), _teclado(juego["letras_intentadas"]), False


def rendirse(user_data: dict) -> str:
    juego = user_data.pop(_CLAVE_ESTADO, None)
    if juego is None:
        return texts.AHORCADO_SIN_JUEGO
    return texts.AHORCADO_RENDIRSE.format(palabra=juego["palabra"])


def palabra_actual(user_data: dict) -> str | None:
    juego = user_data.get(_CLAVE_ESTADO)
    return juego["palabra"] if juego else None
