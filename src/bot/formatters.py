"""Arma el mensaje de Telegram combinando RAE + Wikcionario. El texto de
cada acepción/definición sale TAL CUAL de las fuentes (src/services/) --
aquí solo se decide el orden, la numeración y el envoltorio de Markdown."""
from src.bot import texts


def _escapar(texto: str) -> str:
    """Escapa los caracteres especiales de Markdown clásico de Telegram."""
    for caracter in ('_', '*', '[', ']'):
        texto = texto.replace(caracter, f'\\{caracter}')
    return texto


_MAX_SINONIMOS_MOSTRADOS = 5


def _lista_acepciones(items: list[dict]) -> str:
    lineas = []
    for i, item in enumerate(items, start=1):
        texto = _escapar(item["texto"])
        etiqueta = item.get("etiqueta")
        if etiqueta:
            lineas.append(f"{i}. _{_escapar(etiqueta)}_ {texto}")
        else:
            lineas.append(f"{i}. {texto}")

        for ejemplo in item.get("ejemplos") or []:
            lineas.append(f"    💬 _{_escapar(ejemplo)}_")

        sinonimos = item.get("sinonimos") or []
        if sinonimos:
            mostrados = ", ".join(_escapar(s) for s in sinonimos[:_MAX_SINONIMOS_MOSTRADOS])
            lineas.append(f"    🔗 Sinónimos: {mostrados}")
    return "\n".join(lineas)


def formatear_resultado(palabra: str, resultado_rae: dict | None,
                         resultado_wikcionario: dict | None) -> str:
    """
    Arma el mensaje final. Al menos uno de los dos resultados debe existir
    (si ambos son None, usar texts.no_encontrado() en su lugar).
    """
    partes = [texts.intro_resultado(), f"\n*{_escapar(palabra.capitalize())}*\n"]

    if resultado_rae:
        partes.append("📖 *Real Academia Española:*")
        etimologia = resultado_rae.get("etimologia")
        if etimologia:
            partes.append(f"_Origen: {_escapar(etimologia)}_")
        partes.append(_lista_acepciones(resultado_rae["acepciones"]))
    else:
        partes.append(texts.SOLO_WIKCIONARIO)

    partes.append("")

    if resultado_wikcionario:
        partes.append("🔎 *Explicación sencilla (Wikcionario):*")
        partes.append(_lista_acepciones(resultado_wikcionario["definiciones"]))
    else:
        partes.append(texts.SOLO_RAE)

    return "\n".join(partes).strip() + texts.toque_de_fe()
