"""
Controlador de usuario — la capa HTTP (v7).

Traduce excepciones de negocio a códigos:
    ValueError       → 400
    LookupError      → 404
    PermissionError  → 401   ← NUEVO en la v7
"""

from fastapi import APIRouter, HTTPException, Response

from models.usuario import (Credenciales, Usuario, UsuarioActualizar,
                            UsuarioReemplazo)
from servicios.ensamblador import crear_servicio_usuario

router = APIRouter(prefix="/api", tags=["usuario"])


def _error(estado: int, mensaje: str, detalle: str) -> HTTPException:
    return HTTPException(
        status_code=estado,
        detail={"estado": estado, "mensaje": mensaje, "detalle": detalle},
    )


# ----------------------------------------------------------------------
# POST /api/usuario/verificar-contrasena — LO NUEVO DE LA v7
# ----------------------------------------------------------------------
# Va ARRIBA de /usuario/{email} a propósito: FastAPI resuelve las rutas en
# orden, y si estuviera abajo, "verificar-contrasena" entraría como si
# fuera un email.
@router.post("/usuario/verificar-contrasena")
async def verificar_contrasena(credenciales: Credenciales):
    try:
        servicio = crear_servicio_usuario()
        return await servicio.verificar(credenciales.email, credenciales.contrasena)
    except ValueError as excepcion:
        raise _error(400, "Parámetros inválidos.", str(excepcion))
    except LookupError as excepcion:
        raise _error(404, "Usuario no encontrado.", str(excepcion))
    except PermissionError:
        # El detalle NO dice "la contraseña está mal": eso le confirmaría a
        # quien pregunta que el usuario existe. Que la API distinga los dos
        # casos por dentro no obliga a contárselos a quien toca la puerta.
        raise _error(401, "Credenciales inválidas.",
                     "El usuario o la contraseña no coinciden.")
    except Exception as excepcion:
        raise _error(500, "Error al verificar las credenciales.", str(excepcion))


# ----------------------------------------------------------------------
# GET /api/usuario — Listar (SIN contraseñas)
# ----------------------------------------------------------------------
@router.get("/usuario")
async def listar_usuarios(limite: int = 1000):
    try:
        servicio = crear_servicio_usuario()
        filas = await servicio.listar(limite)
        if not filas:
            return Response(status_code=204)
        return {"tabla": "usuario", "limite": limite,
                "total": len(filas), "datos": filas}
    except ValueError as excepcion:
        raise _error(400, "Parámetros inválidos.", str(excepcion))
    except Exception as excepcion:
        raise _error(500, "Error al consultar usuarios.", str(excepcion))


# ----------------------------------------------------------------------
# GET /api/usuario/{email} — Uno, CON sus roles
# ----------------------------------------------------------------------
@router.get("/usuario/{email}")
async def obtener_usuario(email: str):
    try:
        servicio = crear_servicio_usuario()
        return await servicio.obtener(email)
    except ValueError as excepcion:
        raise _error(400, "Parámetros inválidos.", str(excepcion))
    except LookupError as excepcion:
        raise _error(404, "Usuario no encontrado.", str(excepcion))
    except Exception as excepcion:
        raise _error(500, "Error al consultar el usuario.", str(excepcion))


# ----------------------------------------------------------------------
# POST /api/usuario — Crear (la contraseña se guarda CIFRADA)
# ----------------------------------------------------------------------
@router.post("/usuario")
async def crear_usuario(usuario: Usuario):
    try:
        servicio = crear_servicio_usuario()
        await servicio.crear(usuario.email, usuario.contrasena)
        return {"estado": 200, "mensaje": "Usuario creado exitosamente."}
    except ValueError as excepcion:
        raise _error(400, "Datos inválidos.", str(excepcion))
    except Exception as excepcion:
        # Aquí cae el email duplicado: la llave la defiende la base.
        raise _error(500, "No se pudo crear el usuario.", str(excepcion))


# ----------------------------------------------------------------------
# PUT /api/usuario/{email} — Reemplazo COMPLETO
# ----------------------------------------------------------------------
@router.put("/usuario/{email}")
async def reemplazar_usuario(email: str, usuario: UsuarioReemplazo):
    try:
        servicio = crear_servicio_usuario()
        filas = await servicio.cambiar_contrasena(email, usuario.contrasena)
        return {"estado": 200, "mensaje": "Usuario reemplazado exitosamente.",
                "filasAfectadas": filas}
    except ValueError as excepcion:
        raise _error(400, "Parámetros inválidos.", str(excepcion))
    except LookupError as excepcion:
        raise _error(404, "Usuario no encontrado.", str(excepcion))
    except Exception as excepcion:
        raise _error(500, "No se pudo reemplazar el usuario.", str(excepcion))


# ----------------------------------------------------------------------
# PATCH /api/usuario/{email} — Actualización PARCIAL
# ----------------------------------------------------------------------
@router.patch("/usuario/{email}")
async def actualizar_usuario(email: str, usuario: UsuarioActualizar):
    try:
        servicio = crear_servicio_usuario()
        if usuario.contrasena is None:
            raise ValueError("No se envió ningún campo para actualizar.")
        filas = await servicio.cambiar_contrasena(email, usuario.contrasena)
        return {"estado": 200, "mensaje": "Usuario actualizado exitosamente.",
                "filasAfectadas": filas}
    except ValueError as excepcion:
        raise _error(400, "Parámetros inválidos.", str(excepcion))
    except LookupError as excepcion:
        raise _error(404, "Usuario no encontrado.", str(excepcion))
    except Exception as excepcion:
        raise _error(500, "No se pudo actualizar el usuario.", str(excepcion))


# ----------------------------------------------------------------------
# DELETE /api/usuario/{email}
# ----------------------------------------------------------------------
@router.delete("/usuario/{email}")
async def eliminar_usuario(email: str):
    try:
        servicio = crear_servicio_usuario()
        filas = await servicio.eliminar(email)
        return {"estado": 200, "mensaje": "Usuario eliminado exitosamente.",
                "filasEliminadas": filas}
    except ValueError as excepcion:
        raise _error(400, "Parámetros inválidos.", str(excepcion))
    except LookupError as excepcion:
        raise _error(404, "Usuario no encontrado.", str(excepcion))
    except Exception as excepcion:
        raise _error(500, "No se pudo eliminar el usuario.", str(excepcion))
