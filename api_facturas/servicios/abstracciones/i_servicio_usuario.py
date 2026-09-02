"""
Contrato del servicio de usuario (v7). El controller depende de esta
interfaz. Excepciones de negocio: ValueError → 400 · LookupError → 404 ·
PermissionError → 401.
"""

from typing import Protocol


class IServicioUsuario(Protocol):
    """Las operaciones de negocio sobre usuario."""

    async def listar(self, limite: int) -> list[dict]:
        """Hasta `limite` usuarios, sin contraseña. ValueError si limite <= 0."""
        ...

    async def obtener(self, email: str) -> dict:
        """El usuario con sus roles. LookupError si no existe."""
        ...

    async def crear(self, email: str, contrasena: str) -> None:
        """Crea el usuario CIFRANDO la contraseña."""
        ...

    async def cambiar_contrasena(self, email: str, contrasena: str) -> int:
        """Cambia la contraseña, cifrándola. LookupError si no existe."""
        ...

    async def eliminar(self, email: str) -> int:
        """Elimina. LookupError si no existe."""
        ...

    async def verificar(self, email: str, contrasena: str) -> dict:
        """Comprueba las credenciales y devuelve el email con sus roles.

        LookupError si el usuario no existe · PermissionError si la
        contraseña no coincide. Son distintas a propósito, y el controller
        decide qué tanto de esa diferencia se le cuenta a quien preguntó.
        """
        ...
