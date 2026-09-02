"""
Repositorio de persona para MariaDB — la capa de DATOS (v2).

(v3) El CALCO entre motores: la clase gemela de la *PostgreSQL con OTRA
cadena de conexión (mysql+aiomysql). El SQL de los moldes es idéntico —
SQLAlchemy con text() y :parametros absorbe el dialecto.

CALCADO del repositorio de producto de la v1: SQLAlchemy async como
ejecutor, SQL visible y parametrizado con text().
"""

from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class RepositorioPersonaMariaDB:
    """Implementación concreta de IRepositorioPersona contra MariaDB."""

    def __init__(self, cadena_conexion: str):
        self._cadena_conexion = cadena_conexion
        self._engine: AsyncEngine | None = None

    def _obtener_engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(self._cadena_conexion)
        return self._engine

    @staticmethod
    def _serializar(fila: dict) -> dict:
        return {
            columna: (float(valor) if isinstance(valor, Decimal) else valor)
            for columna, valor in fila.items()
        }

    async def obtener_todos(self, limite: int) -> list[dict]:
        sql = text(
            "SELECT codigo, nombre, email, telefono "
            "FROM persona ORDER BY codigo LIMIT :limite"
        )
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"limite": limite})
            return [self._serializar(dict(fila._mapping)) for fila in resultado]

    async def obtener_por_codigo(self, codigo: str) -> dict | None:
        sql = text(
            "SELECT codigo, nombre, email, telefono "
            "FROM persona WHERE codigo = :codigo"
        )
        async with self._obtener_engine().connect() as conexion:
            resultado = await conexion.execute(sql, {"codigo": codigo})
            fila = resultado.first()
            return self._serializar(dict(fila._mapping)) if fila else None

    async def crear(self, datos: dict) -> bool:
        sql = text(
            "INSERT INTO persona (codigo, nombre, email, telefono) VALUES (:codigo, :nombre, :email, :telefono)"
        )
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(sql, datos)
            return resultado.rowcount == 1

    async def actualizar(self, codigo: str, datos: dict) -> int:
        asignaciones = ", ".join(f"{columna} = :{columna}" for columna in datos)
        sql = text(
            f"UPDATE persona SET {asignaciones} WHERE codigo = :pk_clave"
        )
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(
                sql, {**datos, "pk_clave": codigo}
            )
            return resultado.rowcount

    async def eliminar(self, codigo: str) -> int:
        # Si la persona es cliente o vendedor, la FK rechaza → 500.
        sql = text("DELETE FROM persona WHERE codigo = :codigo")
        async with self._obtener_engine().begin() as conexion:
            resultado = await conexion.execute(sql, {"codigo": codigo})
            return resultado.rowcount
