import json
import urllib.error
from unittest.mock import patch, MagicMock

import pytest

from src.services.rae import buscar_rae

RESPUESTA_CASA = {
    "data": {
        "word": "casa",
        "meanings": [
            {
                "origin": {"raw": "Del lat. casa 'choza'."},
                "senses": [
                    {
                        "description": "Edificio para habitar",
                        "category": "noun",
                        "gender": "feminine",
                        "examples": ["Una casa de ocho plantas."],
                        "synonyms": ["vivienda", "inmueble", "domicilio"],
                    },
                    {
                        "description": "Edificio de una o pocas plantas destinado a vivienda unifamiliar",
                        "category": "noun",
                        "gender": "feminine",
                    },
                ]
            }
        ],
    }
}


def _fake_response(payload: dict):
    fake_resp = MagicMock()
    fake_resp.read.return_value = json.dumps(payload).encode("utf-8")
    fake_resp.__enter__.return_value = fake_resp
    return fake_resp


def test_buscar_rae_encontrada():
    with patch("urllib.request.urlopen", return_value=_fake_response(RESPUESTA_CASA)):
        resultado = buscar_rae("casa")
    assert resultado is not None
    assert resultado["palabra"] == "casa"
    assert len(resultado["acepciones"]) == 2
    assert resultado["acepciones"][0]["texto"] == "Edificio para habitar"
    assert resultado["acepciones"][0]["etiqueta"] == "f."


def test_buscar_rae_incluye_etimologia_ejemplos_y_sinonimos():
    with patch("urllib.request.urlopen", return_value=_fake_response(RESPUESTA_CASA)):
        resultado = buscar_rae("casa")
    assert resultado["etimologia"] == "Del lat. casa 'choza'."
    assert resultado["acepciones"][0]["ejemplos"] == ["Una casa de ocho plantas."]
    assert resultado["acepciones"][0]["sinonimos"] == ["vivienda", "inmueble", "domicilio"]
    assert resultado["acepciones"][1]["ejemplos"] == []
    assert resultado["acepciones"][1]["sinonimos"] == []


def test_buscar_rae_no_encontrada_404():
    error = urllib.error.HTTPError(url="", code=404, msg="Not Found", hdrs=None, fp=None)
    with patch("urllib.request.urlopen", side_effect=error):
        assert buscar_rae("asdfqwerty123") is None


def test_buscar_rae_error_servidor_lanza_excepcion():
    error = urllib.error.HTTPError(url="", code=500, msg="Server Error", hdrs=None, fp=None)
    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(RuntimeError):
            buscar_rae("casa")


def test_max_acepciones_limita_resultado():
    with patch("urllib.request.urlopen", return_value=_fake_response(RESPUESTA_CASA)):
        resultado = buscar_rae("casa", max_acepciones=1)
    assert len(resultado["acepciones"]) == 1
