import json
from unittest.mock import patch, MagicMock

from src.services.wikcionario import buscar_wikcionario, _seccion_espanol

EXTRACTO_CASA = """
== Español ==


=== Etimología 1 ===
Del latín casa ('choza'), de origen incierto.


==== Sustantivo femenino ====
casa | plural: casas

1 Vivienda
Edificación destinada a vivienda.
2
Domicilio.
Sinónimos: domicilio, hogar, lar, morada, residencia, vivienda
3
Piso, departamento o local.


== Referencias y notas ==
"""


def _respuesta_json(pages: dict) -> bytes:
    return json.dumps({"batchcomplete": "", "query": {"pages": pages}}).encode("utf-8")


def test_seccion_espanol_extrae_solo_esa_seccion():
    seccion = _seccion_espanol(EXTRACTO_CASA)
    assert seccion is not None
    assert "Vivienda" in seccion
    assert "Referencias y notas" not in seccion


def test_buscar_wikcionario_palabra_no_encontrada():
    pages = {"-1": {"ns": 0, "title": "asdfqwerty", "missing": ""}}
    fake_resp = MagicMock()
    fake_resp.read.return_value = _respuesta_json(pages)
    fake_resp.__enter__.return_value = fake_resp
    with patch("urllib.request.urlopen", return_value=fake_resp):
        assert buscar_wikcionario("asdfqwerty") is None


def test_buscar_wikcionario_casa_devuelve_definiciones():
    pages = {"7665": {"pageid": 7665, "ns": 0, "title": "casa", "extract": EXTRACTO_CASA}}
    fake_resp = MagicMock()
    fake_resp.read.return_value = _respuesta_json(pages)
    fake_resp.__enter__.return_value = fake_resp
    with patch("urllib.request.urlopen", return_value=fake_resp):
        resultado = buscar_wikcionario("casa")
    assert resultado is not None
    assert resultado["palabra"] == "casa"
    assert len(resultado["definiciones"]) == 3
    assert "Edificación destinada a vivienda." in resultado["definiciones"][0]["texto"]
    assert resultado["definiciones"][0]["etiqueta"] == "Vivienda"
    assert resultado["definiciones"][1]["etiqueta"] is None
