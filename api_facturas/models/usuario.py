"""
Modelos Pydantic de la entidad usuario — la FRONTERA DE ENTRADA de la API.

La llave es el email, no un id generado: así lo declara la tabla.

OJO con `contrasena`: lo que entra por aquí es la contraseña EN CLARO que
escribió alguien, y lo que se guarda es su hash. La API nunca devuelve el
campo — ni el hash ni la clara — porque un endpoint que devuelve
contraseñas es un endpoint que las filtra.
"""

from pydantic import BaseModel, EmailStr, Field


class Usuario(BaseModel):
    """POST /api/usuario — los dos campos son obligatorios."""

    email: EmailStr
    contrasena: str = Field(min_length=1, max_length=200)


class UsuarioReemplazo(BaseModel):
    """PUT /api/usuario/{email} — el email va en la ruta, no en el cuerpo."""

    contrasena: str = Field(min_length=1, max_length=200)


class UsuarioActualizar(BaseModel):
    """PATCH /api/usuario/{email} — parcial.

    Hoy usuario tiene un solo campo modificable, así que PATCH y PUT hacen
    lo mismo. Se mantienen separados igual, porque lo que los distingue no
    es cuántos campos hay hoy: es su SEMÁNTICA. El día que la tabla gane
    una columna, PUT seguirá exigiéndolo todo y PATCH no — sin tocar nada.
    """

    contrasena: str | None = Field(default=None, min_length=1, max_length=200)


class Credenciales(BaseModel):
    """POST /api/usuario/verificar-contrasena — lo que manda un login."""

    email: EmailStr
    contrasena: str = Field(min_length=1)
