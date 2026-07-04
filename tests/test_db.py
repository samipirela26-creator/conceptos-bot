from src.db import DBClient


def _db():
    return DBClient(":memory:")


def test_agregar_y_listar_favorito():
    db = _db()
    assert db.agregar_favorito(1, "Casa") is True
    assert db.listar_favoritos(1) == ["casa"]


def test_agregar_favorito_duplicado_devuelve_false():
    db = _db()
    db.agregar_favorito(1, "casa")
    assert db.agregar_favorito(1, "casa") is False
    assert db.listar_favoritos(1) == ["casa"]


def test_quitar_favorito():
    db = _db()
    db.agregar_favorito(1, "casa")
    assert db.quitar_favorito(1, "casa") is True
    assert db.listar_favoritos(1) == []


def test_quitar_favorito_inexistente_devuelve_false():
    db = _db()
    assert db.quitar_favorito(1, "casa") is False


def test_es_favorito():
    db = _db()
    assert db.es_favorito(1, "casa") is False
    db.agregar_favorito(1, "casa")
    assert db.es_favorito(1, "casa") is True


def test_favoritos_aislados_por_usuario():
    db = _db()
    db.agregar_favorito(1, "casa")
    assert db.listar_favoritos(2) == []


def test_registrar_y_listar_historial_orden_reciente_primero():
    db = _db()
    db.registrar_historial(1, "casa")
    db.registrar_historial(1, "perro")
    assert db.listar_historial(1) == ["perro", "casa"]


def test_historial_no_repite_palabras():
    db = _db()
    db.registrar_historial(1, "casa")
    db.registrar_historial(1, "perro")
    db.registrar_historial(1, "casa")
    assert db.listar_historial(1) == ["casa", "perro"]


def test_historial_respeta_limite():
    db = _db()
    for palabra in ["a", "b", "c", "d"]:
        db.registrar_historial(1, palabra)
    assert db.listar_historial(1, limite=2) == ["d", "c"]
