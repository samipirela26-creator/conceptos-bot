"""Cliente Gemini con un ÚNICO propósito: extraer de un mensaje libre la
palabra/concepto que la persona quiere que se le defina. NUNCA se usa para
redactar ni reformular la definición en sí -- esa siempre sale tal cual de
RAE (rae-api.com) y Wikcionario (src/services/). Solo stdlib (urllib), mismo
patrón de resiliencia (varios modelos, se salta al siguiente si uno se
satura) que asistente-bot/gastos-bot."""
import json
import logging
import re
import socket
import urllib.request
import urllib.error

logger = logging.getLogger('conceptos-bot')

# Se prueban en orden; si uno esta saturado (429/500/503) se pasa al siguiente.
MODELOS = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite",
           "gemini-3.1-flash-lite"]

PROMPT = """Un usuario le escribió esto a un bot de definiciones en Telegram:
"{mensaje}"

Tu única tarea es identificar CUÁL es la palabra o concepto puntual que
quiere que le definan (ignora saludos, cortesías y relleno). Si el mensaje
ya es directamente una palabra o frase corta, esa es el concepto.
Si el mensaje NO pide definir nada (es un saludo, una charla casual, o no
se entiende qué palabra busca), responde con concepto null.

Responde ÚNICAMENTE con este JSON, sin explicaciones:
{{"concepto": "palabra o null"}}"""


def _url(modelo: str) -> str:
    return (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{modelo}:generateContent"
    )


class GeminiClient:
    """Extrae el concepto/palabra de un mensaje libre usando Gemini."""

    def __init__(self, api_key: str, model: str = 'gemini-3.5-flash'):
        self.api_key = api_key
        self.model_name = model

    def _modelos_a_probar(self):
        vistos = {self.model_name}
        yield self.model_name
        for modelo in MODELOS:
            if modelo not in vistos:
                vistos.add(modelo)
                yield modelo

    def extraer_concepto(self, mensaje: str) -> str | None:
        """
        Devuelve la palabra/concepto detectado, o None si no aplica o si
        Gemini no está disponible (el llamador debe tener un respaldo
        heurístico para este último caso).
        """
        cuerpo = {
            "contents": [{"role": "user", "parts": [{"text": PROMPT.format(mensaje=mensaje)}]}],
        }
        datos = json.dumps(cuerpo).encode('utf-8')

        texto_respuesta = None
        for modelo in self._modelos_a_probar():
            req = urllib.request.Request(
                _url(modelo) + f"?key={self.api_key}",
                data=datos,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    out = json.loads(resp.read().decode('utf-8'))
                texto_respuesta = out["candidates"][0]["content"]["parts"][0]["text"]
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 503):
                    logger.warning(f"Modelo {modelo} saturado ({e.code}), probando siguiente")
                    continue
                logger.error(f"Error HTTP de Gemini ({modelo}): {e.code}")
                return None
            except (socket.timeout, urllib.error.URLError, TimeoutError,
                     KeyError, IndexError, json.JSONDecodeError) as e:
                logger.warning(f"Fallo con modelo {modelo}: {e}")
                continue

        if not texto_respuesta:
            logger.error("Ningún modelo de Gemini respondió para extraer el concepto")
            return None

        match = re.search(r'\{.*\}', texto_respuesta, re.DOTALL)
        if not match:
            return None
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None

        concepto = data.get("concepto")
        if not concepto or str(concepto).strip().lower() in ("null", "none", ""):
            return None
        return str(concepto).strip()
