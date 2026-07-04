"""Cliente para Wikcionario en español (es.wiktionary.org), licencia
CC BY-SA. Se usa la API pública de MediaWiki (action=query&prop=extracts)
que devuelve el artículo ya en texto plano, sin wikitexto crudo. Solo
extraemos la sección "== Español ==" y sus definiciones numeradas: nunca
se genera ni reescribe contenido, solo se recorta el texto real."""
import json
import logging
import re
import urllib.parse
import urllib.request
import urllib.error

logger = logging.getLogger('conceptos-bot')

API_URL = "https://es.wiktionary.org/w/api.php"

# Ej: "1 Vivienda\nEdificación destinada a vivienda." o "2\nDomicilio."
# OJO: usar solo [ \t]* (no \s*) entre el número y la etiqueta -- \s* también
# matchea saltos de línea y se comía el separador real cuando no hay
# etiqueta en la misma línea (caso "2\nDomicilio."), corriendo el resto del
# parseo una línea de más.
_DEFINICION_RE = re.compile(r'\n(\d+)[ \t]*([^\n]*)\n([^\n=][^\n]*)')


def _seccion_espanol(extracto: str) -> str | None:
    match = re.search(r'\n==\s*Español\s*==\n(.*?)(?=\n==\s*[^=]|\Z)', extracto, re.DOTALL)
    return match.group(1) if match else None


def buscar_wikcionario(palabra: str, max_definiciones: int = 3) -> dict | None:
    """
    Busca una palabra en Wikcionario español.

    Returns:
        None si la palabra no tiene entrada, o no tiene sección en español.
        dict {"palabra": str, "definiciones": [str, ...]} si existe.

    Raises:
        RuntimeError si hay un problema de red/servicio.
    """
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": palabra.lower(),
        "prop": "extracts",
        "format": "json",
        "explaintext": 1,
        "redirects": 1,
    })
    req = urllib.request.Request(f"{API_URL}?{params}",
                                  headers={"User-Agent": "conceptos-bot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode('utf-8'))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        logger.error(f"Error consultando Wikcionario para '{palabra}': {e}")
        raise RuntimeError(f"No se pudo conectar con Wikcionario: {e}")

    paginas = body.get("query", {}).get("pages", {})
    pagina = next(iter(paginas.values()), None)
    if not pagina or "missing" in pagina:
        return None

    extracto = pagina.get("extract", "")
    seccion = _seccion_espanol(extracto)
    if not seccion:
        return None

    definiciones = []
    vistos_numeros = set()
    for numero, etiqueta, texto in _DEFINICION_RE.findall(seccion):
        if numero in vistos_numeros:
            continue
        texto = texto.strip()
        etiqueta = etiqueta.strip()
        if not texto:
            continue
        vistos_numeros.add(numero)
        definiciones.append({"texto": texto, "etiqueta": etiqueta or None})
        if len(definiciones) >= max_definiciones:
            break

    if not definiciones:
        return None

    return {"palabra": pagina.get("title", palabra), "definiciones": definiciones}
