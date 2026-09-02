"""
Contrato del repositorio de usuario (v7). El servicio depende de ESTA
interfaz, nunca de una clase concreta (inversión de dependencias).
"""

from typing import Protocol


class IRepositorioUsuario(Protocol):
    """Las operaciones de datos de la entidad usuario."""

    async def obtener_todos(self, limite: int) -> list[dict]:
        """Hasta `limite` usuarios, SIN la contraseña."""
        ...

    async def obtener_por_email(self, email: str) -> dict | None:
        """El usuario con ese email (sin contraseña), o None."""
        ...

    async def obtener_hash(self, email: str) -> str | None:
        """Lo que está GUARDADO en la columna contrasena, o None.

        Existe aparte de `obtener_por_email` a propósito: es la única
        operación que saca ese valor de la base, y solo la usa la
        verificación. Así no viaja por accidente en un listado.
        """
        ...

    async def obtener_roles(self, email: str) -> list[str]:
        """Los nombres de los roles del usuario (puede ser lista vacía)."""
        ...

    async def crear(self, email: str, hash_contrasena: str) -> bool:
        """Inserta el usuario con la contraseña YA cifrada."""
        ...

    async def actualizar_contrasena(self, email: str, hash_contrasena: str) -> int:
        """Cambia la contraseña (ya cifrada). Devuelve filas afectadas."""
        ...

    async def eliminar(self, email: str) -> int:
        """Elimina. Devuelve filas eliminadas (0 = no existía)."""
        ...
