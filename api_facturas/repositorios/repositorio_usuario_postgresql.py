"""
Repositorio de usuario para PostgreSQL — la capa de DATOS (v7).

CALCADO del repositorio de empresa: SQLAlchemy async como ejecutor, SQL
visible y parametrizado con text().

Fíjese en lo que este archivo NO hace: no cifra, no compara contraseñas y
no decide si alguien puede entrar. Solo lee y escribe lo que le pidan. Un
repositorio que supiera de bcrypt sería un repositorio con negocio adentro.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class RepositorioUsuarioPostgreSQL:
    """Implementación concreta de IRepositorioUsuario contra PostgreSQL."""

    def __init__(self, cadena_conexion: str):
        self._cadena_conexion = cadena_conexion
        self._engine: AsyncEngine | None = None

    def _obtener_engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(self._cadena_conexion)
        return self._engine

    async def obtener_todos(self, limite: int) -> list[dict]:
        # La contraseña NO se selecciona: lo que no se lee, no se filtra.
        sql = text(
            "SELECT email FROM usuario ORDER BY email LIMIT :limite"
        )
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"limite": limite})
            return [dict(fila._mapping) for fila in resultado]

    async def obtener_por_email(self, email: str) -> dict | None:
        sql = text("SELECT email FROM usuario WHERE email = :email")
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"email": email})
            fila = resultado.first()
            return dict(fila._mapping) if fila else None

    async def obtener_hash(self, email: str) -> str | None:
        """La ÚNICA consulta que saca la columna contrasena de la base."""
        sql = text("SELECT contrasena FROM usuario WHERE email = :email")
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"email": email})
            fila = resultado.first()
            return fila[0] if fila else None

    async def obtener_roles(self, email: str) -> list[str]:
        # El JOIN lo hace quien tiene los datos, no el que pregunta.
        sql = text(
            "SELECT r.nombre "
            "FROM rol_usuario ru "
            "JOIN rol r ON r.id = ru.fkidrol "
            "WHERE ru.fkemail = :email "
            "ORDER BY r.nombre"
        )
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"email": email})
            return [fila[0] for fila in resultado]

    async def crear(self, email: str, hash_contrasena: str) -> bool:
        sql = text(
            "INSERT INTO usuario (email, contrasena) "
            "VALUES (:email, :contrasena)"
        )
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(
                sql, {"email": email, "contrasena": hash_contrasena})
            return resultado.rowcount == 1

    async def actualizar_contrasena(self, email: str, hash_contrasena: str) -> int:
        sql = text(
            "UPDATE usuario SET contrasena = :contrasena WHERE email = :email"
        )
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(
                sql, {"email": email, "contrasena": hash_contrasena})
            return resultado.rowcount

    async def eliminar(self, email: str) -> int:
        # Si el usuario tiene roles asignados, la FK de rol_usuario rechaza
        # el borrado → 500. La integridad la defiende la base.
        sql = text("DELETE FROM usuario WHERE email = :email")
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(sql, {"email": email})
            return resultado.rowcount
