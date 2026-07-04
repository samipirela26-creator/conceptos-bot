"""Extrae el concepto/palabra a buscar de un mensaje, sin usar IA. Cubre el
caso más común (el usuario escribe la palabra directa, o una pregunta con
fórmula predecible: "qué es X", "qué significa X", "define X"). Si el
mensaje no encaja en ningún patrón, el llamador debe recurrir a Gemini
(src/llm/gemini_client.py) como respaldo -- ver src/bot/handlers.py."""
import re

_ARTICULO = r'(?:el|la|los|las|un|una|unos|unas)\s+'

_PREFIJOS = [
    rf'^qu[ée]\s+es\s+(?:{_ARTICULO})?',
    rf'^qu[ée]\s+significa\s+(?:{_ARTICULO})?',
    rf'^qu[ée]\s+quiere\s+decir\s+(?:{_ARTICULO})?',
    rf'^significado\s+de\s+(?:{_ARTICULO})?',
    rf'^defin[ei]\s+(?:{_ARTICULO})?',
    rf'^define\s+(?:{_ARTICULO})?',
]

_MAX_PALABRAS_DIRECTAS = 3


def extraer_heuristico(mensaje: str) -> str | None:
    """Devuelve el concepto si el mensaje encaja en un patrón simple y
    predecible, o None si hace falta ayuda de IA para entenderlo."""
    texto = mensaje.strip().strip('¿?¡!.').strip()
    if not texto:
        return None

    minuscula = texto.lower()
    for patron in _PREFIJOS:
        match = re.match(patron, minuscula)
        if match:
            resto = texto[match.end():].strip().strip('¿?¡!.').strip()
            return resto or None

    # Sin fórmula de pregunta: si es corto (típico de escribir la palabra
    # directo), se toma tal cual. Si es una frase larga, mejor que lo
    # interprete Gemini en vez de arriesgarse a extraer basura.
    if len(texto.split()) <= _MAX_PALABRAS_DIRECTAS and '?' not in mensaje:
        return texto

    return None
