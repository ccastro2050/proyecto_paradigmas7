"""
Servicio de usuario — la capa de NEGOCIO (v7).

Es el primer servicio del proyecto que hace algo más que ordenar llamadas:
**cifra y comprueba contraseñas**. Y esa es exactamente la capa donde debe
estar. Ni el controller (que solo habla HTTP) ni el repositorio (que solo
habla con un motor) tienen por qué saber qué es bcrypt.
"""

import bcrypt

from repositorios.abstracciones.i_repositorio_usuario import IRepositorioUsuario


class ServicioUsuario:
    """Reglas de negocio de usuario, incluida la verificación de acceso."""

    def __init__(self, repositorio: IRepositorioUsuario):
        self._repositorio = repositorio

    # ------------------------------------------------------------------
    # Las contraseñas
    # ------------------------------------------------------------------
    @staticmethod
    def _cifrar(contrasena: str) -> str:
        """El hash que se guarda. NUNCA se guarda la contraseña en claro."""
        return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode()

    @staticmethod
    def _coincide(contrasena: str, guardado: str) -> bool:
        """¿La contraseña corresponde a lo guardado?

        Los datos que trae la base NO son homogéneos: unos usuarios tienen
        un hash bcrypt ('$2a$…', '$2b$…') y otros tienen la contraseña EN
        CLARO ('jefe123', 'cli123'). Eso no es una decisión de diseño: es
        una inconsistencia de los datos dados, y está registrada como
        clarificación C1 de la v7.

        Se aceptan las dos formas para que el sistema funcione con los datos
        que hay, PERO todo lo que esta API escriba de ahora en adelante va
        cifrado. Los usuarios en claro son deuda: se van cuando alguien les
        cambie la contraseña.
        """
        if guardado.startswith(("$2a$", "$2b$", "$2y$")):
            try:
                return bcrypt.checkpw(contrasena.encode("utf-8"), guardado.encode("utf-8"))
            except ValueError:
                # Un hash corrupto no es una contraseña válida, y tampoco
                # una excepción que deba tumbar el login.
                return False
        return contrasena == guardado

    @staticmethod
    def _validar_email(email: str) -> str:
        email = (email or "").strip()
        if not email:
            raise ValueError("El email del usuario no puede estar vacío.")
        return email

    # ------------------------------------------------------------------
    # El CRUD
    # ------------------------------------------------------------------
    async def listar(self, limite: int) -> list[dict]:
        if limite <= 0:
            raise ValueError("El límite debe ser un entero mayor que cero.")
        return await self._repositorio.obtener_todos(limite)

    async def obtener(self, email: str) -> dict:
        email = self._validar_email(email)
        fila = await self._repositorio.obtener_por_email(email)
        if fila is None:
            raise LookupError(f"No existe un usuario con email = {email}")
        fila["roles"] = await self._repositorio.obtener_roles(email)
        return fila

    async def crear(self, email: str, contrasena: str) -> None:
        await self._repositorio.crear(email, self._cifrar(contrasena))

    async def cambiar_contrasena(self, email: str, contrasena: str) -> int:
        email = self._validar_email(email)
        filas = await self._repositorio.actualizar_contrasena(
            email, self._cifrar(contrasena))
        if filas == 0:
            raise LookupError(f"No existe un usuario con email = {email}")
        return filas

    async def eliminar(self, email: str) -> int:
        email = self._validar_email(email)
        filas = await self._repositorio.eliminar(email)
        if filas == 0:
            raise LookupError(f"No existe un usuario con email = {email}")
        return filas

    # ------------------------------------------------------------------
    # La verificación: lo nuevo de la v7
    # ------------------------------------------------------------------
    async def verificar(self, email: str, contrasena: str) -> dict:
        """Comprueba las credenciales y devuelve el email con sus roles."""
        email = self._validar_email(email)

        guardado = await self._repositorio.obtener_hash(email)
        if guardado is None:
            raise LookupError(f"No existe un usuario con email = {email}")

        if not self._coincide(contrasena, guardado):
            raise PermissionError("La contraseña no coincide.")

        return {"email": email, "roles": await self._repositorio.obtener_roles(email)}
