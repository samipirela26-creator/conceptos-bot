from src.utils.concept_extractor import extraer_heuristico


def test_palabra_directa():
    assert extraer_heuristico("casa") == "casa"


def test_palabra_con_espacios():
    assert extraer_heuristico("  fotosíntesis  ") == "fotosíntesis"


def test_que_es():
    assert extraer_heuristico("¿qué es la fotosíntesis?") == "fotosíntesis"


def test_que_significa():
    assert extraer_heuristico("qué significa ósmosis") == "ósmosis"


def test_significado_de():
    assert extraer_heuristico("significado de ósmosis") == "ósmosis"


def test_define():
    assert extraer_heuristico("define entropía") == "entropía"


def test_frase_larga_sin_patron_devuelve_none():
    # Frase larga y ambigua: debe delegarse a Gemini, no adivinar.
    assert extraer_heuristico("oye no entiendo bien qué me quisiste decir ayer") is None


def test_vacio_devuelve_none():
    assert extraer_heuristico("   ") is None
