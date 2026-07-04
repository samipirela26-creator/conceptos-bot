"""Cliente SQLite para favoritos e historial de búsquedas. Cada usuario
(user_id de Telegram) tiene sus propios favoritos e historial, aislados
entre sí."""
import logging
import sqlite3

logger = logging.getLogger('conceptos-bot')


class DBClient:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS favoritos (
                user_id INTEGER NOT NULL,
                palabra TEXT NOT NULL,
                fecha TEXT NOT NULL DEFAULT (datetime('now')),
                PRIMARY KEY (user_id, palabra)
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                palabra TEXT NOT NULL,
                fecha TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id INTEGER PRIMARY KEY
            )
        """)
        self._conn.commit()
        logger.info(f"Base de datos SQLite lista en: {db_path}")

    def close(self):
        self._conn.close()

    def agregar_favorito(self, user_id: int, palabra: str) -> bool:
        """Devuelve True si se agregó, False si ya era favorito."""
        try:
            self._conn.execute(
                "INSERT INTO favoritos (user_id, palabra) VALUES (?, ?)",
                (user_id, palabra.lower()),
            )
            self._conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def quitar_favorito(self, user_id: int, palabra: str) -> bool:
        """Devuelve True si existía y se quitó, False si no estaba."""
        cursor = self._conn.execute(
            "DELETE FROM favoritos WHERE user_id = ? AND palabra = ?",
            (user_id, palabra.lower()),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def es_favorito(self, user_id: int, palabra: str) -> bool:
        cursor = self._conn.execute(
            "SELECT 1 FROM favoritos WHERE user_id = ? AND palabra = ?",
            (user_id, palabra.lower()),
        )
        return cursor.fetchone() is not None

    def listar_favoritos(self, user_id: int) -> list[str]:
        cursor = self._conn.execute(
            "SELECT palabra FROM favoritos WHERE user_id = ? ORDER BY fecha DESC",
            (user_id,),
        )
        return [fila[0] for fila in cursor.fetchall()]

    def registrar_historial(self, user_id: int, palabra: str) -> None:
        self._conn.execute(
            "INSERT INTO historial (user_id, palabra) VALUES (?, ?)",
            (user_id, palabra.lower()),
        )
        self._conn.commit()

    def listar_historial(self, user_id: int, limite: int = 10) -> list[str]:
        """Últimas palabras buscadas, sin repetir, más reciente primero."""
        cursor = self._conn.execute(
            "SELECT palabra, MAX(id) AS ultimo_id FROM historial "
            "WHERE user_id = ? GROUP BY palabra ORDER BY ultimo_id DESC LIMIT ?",
            (user_id, limite),
        )
        return [fila[0] for fila in cursor.fetchall()]

    def registrar_usuario(self, user_id: int) -> None:
        """Registra que este user_id ya interactuó con el bot -- se usa para
        saber a quién enviarle la 'palabra del día' cuando el registro es
        abierto (ALLOWED_USER_IDS vacío) y no hay una lista fija de destinatarios."""
        self._conn.execute(
            "INSERT OR IGNORE INTO usuarios (user_id) VALUES (?)", (user_id,)
        )
        self._conn.commit()

    def listar_usuarios(self) -> list[int]:
        cursor = self._conn.execute("SELECT user_id FROM usuarios")
        return [fila[0] for fila in cursor.fetchall()]
