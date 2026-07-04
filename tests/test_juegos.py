from src.bot import juegos, texts
from src.bot.juegos_data import CATEGORIAS, JUEGOS


def test_teclado_categorias_tiene_las_diez_categorias():
    teclado = juegos.teclado_categorias()
    assert len(teclado.inline_keyboard) == len(CATEGORIAS) == 10


def test_nombre_categoria_existente_y_no_existente():
    assert juegos.nombre_categoria("fe") == "🕊️ Fe y reflexión"
    assert juegos.nombre_categoria("no-existe") is None


def test_teclado_juegos_de_categoria_incluye_boton_volver():
    teclado = juegos.teclado_juegos_de_categoria("fe")
    assert teclado is not None
    ultima_fila = teclado.inline_keyboard[-1]
    assert ultima_fila[0].callback_data == "francis_juegos:categorias"


def test_teclado_juegos_de_categoria_inexistente_devuelve_none():
    assert juegos.teclado_juegos_de_categoria("no-existe") is None


def test_texto_juegos_de_categoria_incluye_titulo_y_descripcion_de_cada_juego():
    texto = juegos.texto_juegos_de_categoria("fe")
    assert texto is not None
    for juego_id, juego in JUEGOS.items():
        if juego["categoria"] == "fe":
            assert juego["titulo"] in texto
            assert juego["descripcion"] in texto


def test_texto_juegos_de_categoria_inexistente_devuelve_none():
    assert juegos.texto_juegos_de_categoria("no-existe") is None


def test_iniciar_juego_arma_estado_y_teclado():
    user_data = {}
    juego_id = next(iter(JUEGOS))
    resultado = juegos.iniciar_juego(user_data, juego_id)
    assert resultado is not None
    mensaje, teclado = resultado
    assert JUEGOS[juego_id]["titulo"] in mensaje
    assert JUEGOS[juego_id]["descripcion"] in mensaje
    assert "juegos" in user_data
    assert len(user_data["juegos"]["pendientes"]) == len(JUEGOS[juego_id]["prompts"]) - 1
    assert len(teclado.inline_keyboard[0]) == 2


def test_iniciar_juego_id_inexistente_devuelve_none():
    assert juegos.iniciar_juego({}, "no-existe") is None


def test_siguiente_prompt_avanza_hasta_agotar_el_juego():
    user_data = {}
    juego_id = "rapidas_ronda_relampago"
    juegos.iniciar_juego(user_data, juego_id)
    total_prompts = len(JUEGOS[juego_id]["prompts"])

    terminado = False
    for _ in range(total_prompts - 1):
        mensaje, teclado, terminado = juegos.siguiente_prompt(user_data)
        assert terminado is False
        assert teclado is not None

    # ya se mostraron todos los prompts -- la siguiente llamada termina el juego
    mensaje, teclado, terminado = juegos.siguiente_prompt(user_data)
    assert terminado is True
    assert teclado is None
    assert "juegos" not in user_data


def test_siguiente_prompt_sin_juego_activo():
    mensaje, teclado, terminado = juegos.siguiente_prompt({})
    assert mensaje == texts.JUEGOS_SIN_JUEGO
    assert teclado is None
    assert terminado is True


def test_salir_juego_termina_y_revela_titulo():
    user_data = {}
    juego_id = "verdad_sincera"
    juegos.iniciar_juego(user_data, juego_id)
    mensaje = juegos.salir_juego(user_data)
    assert JUEGOS[juego_id]["titulo"] in mensaje
    assert "juegos" not in user_data


def test_salir_juego_sin_juego_activo():
    assert juegos.salir_juego({}) == texts.JUEGOS_SIN_JUEGO


def test_juego_actual():
    user_data = {}
    assert juegos.juego_actual(user_data) is None
    juegos.iniciar_juego(user_data, "fe_gratitud_diaria")
    assert juegos.juego_actual(user_data) == "fe_gratitud_diaria"


def test_catalogo_tiene_cien_juegos_diez_prompts_cada_uno():
    assert len(JUEGOS) == 100
    for juego in JUEGOS.values():
        assert len(juego["prompts"]) == 10
        assert len(set(juego["prompts"])) == 10


def test_catalogo_todos_los_juegos_tienen_descripcion():
    for juego in JUEGOS.values():
        assert isinstance(juego.get("descripcion"), str)
        assert len(juego["descripcion"].strip()) > 0
