"""Cliente para la API comunitaria rae-api.com (scrapea dle.rae.es y
devuelve JSON limpio). Solo stdlib (urllib), mismo patrón que los otros
bots del usuario. Nunca genera texto: siempre devuelve la definición real
tal cual la trae la RAE."""
import json
import logging
import urllib.parse
import urllib.request
import urllib.error

logger = logging.getLogger('conceptos-bot')

BASE_URL = "https://rae-api.com/api/words/"


def buscar_rae(palabra: str, max_acepciones: int = 3) -> dict | None:
    """
    Busca una palabra en la RAE vía rae-api.com.

    Returns:
        None si la palabra no existe en la RAE.
        dict {"palabra": str, "acepciones": [str, ...]} si existe.

    Raises:
        RuntimeError si hay un problema de red/servicio (no de "no encontrado").
    """
    url = BASE_URL + urllib.parse.quote(palabra.lower())
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        logger.error(f"rae-api.com respondió {e.code} para '{palabra}'")
        raise RuntimeError(f"rae-api.com respondió {e.code}")
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        logger.error(f"Error consultando rae-api.com para '{palabra}': {e}")
        raise RuntimeError(f"No se pudo conectar con rae-api.com: {e}")

    data = body.get("data")
    if not data:
        return None

    acepciones = []
    for meaning in data.get("meanings", []):
        for sense in meaning.get("senses", []):
            texto = (sense.get("description") or "").strip()
            if not texto:
                continue
            categoria = sense.get("category")
            genero = sense.get("gender")
            etiqueta = None
            if categoria == "noun" and genero:
                etiqueta = "f." if genero == "feminine" else "m." if genero == "masculine" else None
            acepciones.append({"texto": texto, "etiqueta": etiqueta})
            if len(acepciones) >= max_acepciones:
                break
        if len(acepciones) >= max_acepciones:
            break

    if not acepciones:
        return None

    return {"palabra": data.get("word", palabra), "acepciones": acepciones}
