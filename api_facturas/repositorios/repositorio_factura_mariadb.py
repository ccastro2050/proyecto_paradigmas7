"""
Repositorio de factura para MariaDB — la API como TRADUCTORA (v3).

El mismo papel que el repositorio PostgreSQL (llamar los SPs de la BD y
traducir), con las dos diferencias del dialecto:

1. MariaDB devuelve el resultado por un parámetro OUT que se recoge con
   una variable de sesión: CALL sp(..., @salida) y luego SELECT @salida —
   dos sentencias sobre LA MISMA conexión/transacción.
2. Los SIGNAL SQLSTATE '45000' de SPs y triggers llegan como DBAPIError
   con código 1644 (ER_SIGNAL_EXCEPTION): aquí (y SOLO aquí) se traducen
   a las MISMAS excepciones de negocio que en PostgreSQL.
"""

import json

from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from excepciones import ConflictoError


class RepositorioFacturaMariaDB:
    """Implementación concreta de IRepositorioFactura contra MariaDB."""

    def __init__(self, cadena_conexion: str):
        self._cadena_conexion = cadena_conexion
        self._engine: AsyncEngine | None = None

    def _obtener_engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_async_engine(self._cadena_conexion)
        return self._engine

    # ------------------------------------------------------------------
    # El ayudante central: CALL + SELECT @salida, y la traducción
    # ------------------------------------------------------------------

    @staticmethod
    def _traducir_si_es_negocio(excepcion: DBAPIError) -> None:
        """Código 1644 (SIGNAL 45000) + patrón del mensaje → negocio."""
        causa = excepcion.orig
        argumentos = getattr(causa, "args", ())
        codigo = argumentos[0] if argumentos else None
        mensaje = str(argumentos[1]) if len(argumentos) > 1 else str(causa)
        if codigo == 1644:
            if "no existe" in mensaje:
                raise LookupError(mensaje)          # → 404
            if "anulada" in mensaje:
                raise ConflictoError(mensaje)       # → 409
        # Lo demás (stock insuficiente del trigger, FK, mínimo de
        # renglones) sube tal cual → 500 con el mensaje del motor.

    async def _ejecutar_sp(self, sql_call: str, parametros: dict) -> dict | list | None:
        try:
            # Las DOS sentencias van sobre la misma conexión: la variable
            # de sesión @salida no existe fuera de ella.
            async with self._obtener_engine().begin() as conexion:
                await conexion.execute(text(sql_call), parametros)
                fila = (await conexion.execute(text("SELECT @salida"))).first()
        except DBAPIError as excepcion:
            self._traducir_si_es_negocio(excepcion)
            raise
        # @salida es LONGTEXT (el JSON de MariaDB): texto → json.loads.
        if fila is None or fila[0] is None:
            return None
        valor = fila[0]
        return json.loads(valor) if isinstance(valor, str) else valor

    # ------------------------------------------------------------------
    # Los 4 métodos del contrato (mismos SPs, mismo JSON)
    # ------------------------------------------------------------------

    async def listar(self) -> list[dict]:
        resultado = await self._ejecutar_sp(
            "CALL sp_listar_facturas_y_productosporfactura(@salida)", {})
        return resultado or []

    async def consultar(self, numero: int) -> dict:
        resultado = await self._ejecutar_sp(
            "CALL sp_consultar_factura_y_productosporfactura(:numero, @salida)",
            {"numero": numero})
        # El mismo aplanado del gemelo PostgreSQL:
        factura = resultado["factura"]
        factura["productos"] = resultado["productos"] or []
        return factura

    async def crear(self, fkidcliente: int, fkidvendedor: int,
                    productos_json: str) -> dict:
        # El JSON de entrada viaja como TEXTO plano: en MariaDB el tipo
        # JSON es un alias de LONGTEXT (no hay cast).
        return await self._ejecutar_sp(
            "CALL sp_insertar_factura_y_productosporfactura("
            ":cliente, :vendedor, :productos, 1, @salida)",
            {"cliente": fkidcliente, "vendedor": fkidvendedor,
             "productos": productos_json})

    async def anular(self, numero: int) -> dict:
        return await self._ejecutar_sp(
            "CALL sp_anular_factura(:numero, @salida)", {"numero": numero})
