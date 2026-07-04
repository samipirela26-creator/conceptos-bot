from src.bot.formatters import formatear_resultado

RAE_CASA = {
    "palabra": "casa",
    "acepciones": [{"texto": "Edificio para habitar", "etiqueta": "f."}],
}
RAE_CASA_ENRIQUECIDA = {
    "palabra": "casa",
    "etimologia": "Del lat. casa 'choza'.",
    "acepciones": [{
        "texto": "Edificio para habitar",
        "etiqueta": "f.",
        "ejemplos": ["Una casa de ocho plantas."],
        "sinonimos": ["vivienda", "inmueble"],
    }],
}
WIKI_CASA = {
    "palabra": "casa",
    "definiciones": [{"texto": "Edificación destinada a vivienda.", "etiqueta": "Vivienda"}],
}


def test_formatear_con_ambas_fuentes():
    mensaje = formatear_resultado("casa", RAE_CASA, WIKI_CASA)
    assert "Real Academia Española" in mensaje
    assert "Wikcionario" in mensaje
    assert "Edificio para habitar" in mensaje
    assert "Edificación destinada a vivienda." in mensaje


def test_formatear_solo_rae():
    mensaje = formatear_resultado("casa", RAE_CASA, None)
    assert "Edificio para habitar" in mensaje
    assert "Wikcionario no conserva entrada" in mensaje


def test_formatear_solo_wikcionario():
    mensaje = formatear_resultado("casa", None, WIKI_CASA)
    assert "Edificación destinada a vivienda." in mensaje
    assert "la Real Academia no tiene entrada" in mensaje


def test_formatear_incluye_toque_de_fe():
    from src.bot import texts
    mensaje = formatear_resultado("casa", RAE_CASA, WIKI_CASA)
    assert any(toque.strip() in mensaje for toque in texts.TOQUE_DE_FE)


def test_formatear_incluye_etimologia_ejemplos_y_sinonimos():
    mensaje = formatear_resultado("casa", RAE_CASA_ENRIQUECIDA, None)
    assert "Del lat. casa 'choza'." in mensaje
    assert "Una casa de ocho plantas." in mensaje
    assert "vivienda, inmueble" in mensaje


def test_formatear_sin_etimologia_ni_ejemplos_no_falla():
    mensaje = formatear_resultado("casa", RAE_CASA, None)
    assert "Edificio para habitar" in mensaje
