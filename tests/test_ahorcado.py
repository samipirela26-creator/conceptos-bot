from src.bot import ahorcado, texts


def _juego(palabra: str, letras_intentadas=None, errores: int = 0) -> dict:
    return {
        "palabra": palabra,
        "letras_intentadas": set(letras_intentadas or []),
        "errores": errores,
    }


def test_normalizar_quita_tildes_pero_no_toca_la_enie():
    assert ahorcado._normalizar("é") == "E"
    assert ahorcado._normalizar("ñ") == "Ñ"
    assert ahorcado._normalizar("a") == "A"


def test_palabra_mostrada_oculta_letras_no_intentadas():
    assert ahorcado._palabra_mostrada("casa", set()) == "_ _ _ _"
    assert ahorcado._palabra_mostrada("casa", {"C", "A"}) == "c a _ a"


def test_palabra_mostrada_revela_letra_con_tilde_al_adivinar_sin_tilde():
    assert ahorcado._palabra_mostrada("océano", {"E"}) == "_ _ é _ _ _"


def test_iniciar_juego_elige_palabra_de_la_lista_y_arma_teclado():
    user_data = {}
    mensaje, teclado = ahorcado.iniciar_juego(user_data)
    assert texts.AHORCADO_INTRO in mensaje
    assert "ahorcado" in user_data
    assert user_data["ahorcado"]["palabra"] in texts.PALABRAS_AHORCADO
    assert len(teclado.inline_keyboard) > 0


def test_procesar_letra_acierto_no_suma_error():
    user_data = {"ahorcado": _juego("casa")}
    mensaje, teclado, terminado = ahorcado.procesar_letra(user_data, "C")
    assert terminado is False
    assert user_data["ahorcado"]["errores"] == 0
    assert "c _ _ _" in mensaje


def test_procesar_letra_fallo_suma_error():
    user_data = {"ahorcado": _juego("casa")}
    mensaje, teclado, terminado = ahorcado.procesar_letra(user_data, "Z")
    assert terminado is False
    assert user_data["ahorcado"]["errores"] == 1


def test_procesar_letra_repetida_no_suma_error_dos_veces():
    user_data = {"ahorcado": _juego("casa")}
    ahorcado.procesar_letra(user_data, "Z")
    ahorcado.procesar_letra(user_data, "Z")
    assert user_data["ahorcado"]["errores"] == 1


def test_procesar_letra_gana_la_partida():
    user_data = {"ahorcado": _juego("casa", letras_intentadas={"C", "S"})}
    mensaje, teclado, terminado = ahorcado.procesar_letra(user_data, "A")
    assert terminado is True
    assert teclado is None
    assert "ahorcado" not in user_data
    assert any(g in mensaje for g in texts.AHORCADO_GANADO)


def test_procesar_letra_pierde_la_partida():
    user_data = {"ahorcado": _juego("casa", letras_intentadas={"X", "Y", "W", "K", "T"}, errores=5)}
    mensaje, teclado, terminado = ahorcado.procesar_letra(user_data, "Z")
    assert terminado is True
    assert teclado is None
    assert "ahorcado" not in user_data
    assert "casa" in mensaje.lower()


def test_procesar_letra_sin_juego_activo():
    mensaje, teclado, terminado = ahorcado.procesar_letra({}, "A")
    assert mensaje == texts.AHORCADO_SIN_JUEGO
    assert teclado is None
    assert terminado is True


def test_rendirse_termina_el_juego_y_revela_palabra():
    user_data = {"ahorcado": _juego("casa")}
    mensaje = ahorcado.rendirse(user_data)
    assert "casa" in mensaje.lower()
    assert "ahorcado" not in user_data


def test_rendirse_sin_juego_activo():
    assert ahorcado.rendirse({}) == texts.AHORCADO_SIN_JUEGO


def test_palabra_actual():
    assert ahorcado.palabra_actual({}) is None
    assert ahorcado.palabra_actual({"ahorcado": _juego("casa")}) == "casa"
