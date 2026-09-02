"""
cliente_api.py — La capa de DATOS del front.

Es al front lo que el repositorio es al back: la ÚNICA pieza que sabe dónde
viven los datos —en la API, nunca en la base— y la única que habla HTTP.
Traduce cada respuesta a `(ok, datos, errores)` para que las vistas no tengan
que saber qué es un 422.

**Lo que cambió en la v6.** La v5 tenía seis funciones para una entidad. Seis
entidades por seis operaciones darían treinta y seis funciones idénticas salvo
el nombre del recurso. En vez de eso hay una clase `Recurso`: cinco objetos
que se distinguen por su nombre y por cómo se llama su llave en la URL.

`factura` NO es un `Recurso`, y por eso tiene sus propias funciones abajo: la
API no le da PUT, ni PATCH, ni DELETE. Una factura no se corrige ni se borra
—es un documento contable—: se **anula**. Forzarla dentro de la clase sería
mentir sobre el contrato.
"""

import os

import requests

# El hostname INTERNO del compose, jamás localhost: dentro de un contenedor,
# localhost es él mismo.
URL_API = os.environ.get("API_FACTURAS_URL", "http://localhost:8021")

TIEMPO_MAXIMO = 10  # segundos

NO_DISPONIBLE = ["El servicio no está disponible. ¿Está arriba la API?"]


def _llamar(metodo: str, ruta: str, **kwargs):
    """Ejecuta la petición y unifica un solo caso: 'la API no responde'.

    Devuelve None cuando NO hubo respuesta —API caída, timeout—, que es
    distinto de 'respondió con un error'. Un 404 es la API funcionando y
    diciendo que no existe; un None es que no hay con quién hablar.
    """
    try:
        return requests.request(
            metodo, f"{URL_API}{ruta}", timeout=TIEMPO_MAXIMO, **kwargs
        )
    except requests.RequestException:
        return None


def _cuerpo(respuesta):
    """El JSON, o un diccionario vacío si no vino JSON.

    Un 500 puede llegar como HTML; sin esto el front se caería justo cuando
    tiene que explicar que algo falló.
    """
    try:
        return respuesta.json()
    except ValueError:
        return {}


def _mensajes(respuesta) -> list[str]:
    """Traduce a texto los DOS formatos de error que produce esta API.

    FastAPI anida siempre bajo `detail`, pero con dos formas distintas:

    1. Los errores que la API escribe a propósito (400, 404, 500):
           {"detail": {"estado": 404, "mensaje": "…", "detalle": "…"}}
    2. Los 422, que genera Pydantic solo, como LISTA:
           {"detail": [{"loc": ["body", "stock"], "msg": "…"}]}

    Conocer las dos es el trabajo de la frontera. Las vistas reciben frases.
    """
    detalle = _cuerpo(respuesta).get("detail")

    if isinstance(detalle, dict):
        partes = [detalle.get("mensaje", ""), detalle.get("detalle", "")]
        return [p for p in partes if p] or ["No se pudo completar la operación."]

    if isinstance(detalle, list):
        frases = []
        for error in detalle:
            campo = error.get("loc", ["", ""])[-1]
            frases.append(f"{campo}: {error.get('msg', 'valor inválido')}")
        return frases or ["Datos inválidos."]

    if isinstance(detalle, str) and detalle:
        return [detalle]

    return ["No se pudo completar la operación."]


class Recurso:
    """Las seis operaciones sobre un recurso REST de la API.

    Un objeto por entidad. Lo único que las distingue es el nombre del recurso
    en la ruta: `/api/producto`, `/api/persona`… Que el CRUD se escriba UNA vez
    no es un truco de programación, es la consecuencia de que la API ofrezca
    **el mismo contrato** para todas: si una se saliera del patrón, no cabría
    aquí — y eso es exactamente lo que pasa con `factura`.
    """

    def __init__(self, nombre: str):
        self.nombre = nombre
        self.base = f"/api/{nombre}"

    def listar(self):
        """GET → (ok, lista, errores). El 204 es 'tabla vacía', no un error."""
        r = _llamar("GET", self.base)
        if r is None:
            return False, [], NO_DISPONIBLE
        if r.status_code == 204:
            return True, [], []
        if r.status_code == 200:
            return True, _cuerpo(r).get("datos", []), []
        return False, [], _mensajes(r)

    def obtener(self, llave):
        """GET /{llave} → (ok, registro, errores)."""
        r = _llamar("GET", f"{self.base}/{llave}")
        if r is None:
            return False, None, NO_DISPONIBLE
        if r.status_code == 200:
            return True, _cuerpo(r), []
        return False, None, _mensajes(r)

    def crear(self, datos: dict):
        """POST → (ok, errores)."""
        r = _llamar("POST", self.base, json=datos)
        if r is None:
            return False, NO_DISPONIBLE
        return (True, []) if r.status_code == 200 else (False, _mensajes(r))

    def reemplazar(self, llave, datos: dict):
        """PUT /{llave} → (ok, errores). TODOS los campos viajan."""
        r = _llamar("PUT", f"{self.base}/{llave}", json=datos)
        if r is None:
            return False, NO_DISPONIBLE
        return (True, []) if r.status_code == 200 else (False, _mensajes(r))

    def actualizar(self, llave, datos: dict):
        """PATCH /{llave} → (ok, errores). Solo viaja lo diligenciado."""
        r = _llamar("PATCH", f"{self.base}/{llave}", json=datos)
        if r is None:
            return False, NO_DISPONIBLE
        return (True, []) if r.status_code == 200 else (False, _mensajes(r))

    def eliminar(self, llave):
        """DELETE /{llave} → (ok, errores)."""
        r = _llamar("DELETE", f"{self.base}/{llave}")
        if r is None:
            return False, NO_DISPONIBLE
        return (True, []) if r.status_code == 200 else (False, _mensajes(r))


_RECURSOS: dict[str, Recurso] = {}


def recurso(nombre: str) -> Recurso:
    """El Recurso de esa entidad, creado la primera vez que se pide.

    Antes esto era un diccionario con la lista de entidades escrita a mano,
    y por tanto una SEGUNDA lista que tenía que coincidir con la de
    `entidades.py`. Al agregar `usuario` en la v7 se agregó allá y se olvidó
    aquí: el menú lo mostraba y la pantalla respondía 500.

    Dos listas que deben coincidir siempre terminan no coincidiendo. La
    corrección no fue agregar la que faltaba —eso deja la trampa puesta para
    la próxima—: fue quitar la segunda lista. Construir un Recurso no abre
    conexiones ni cuesta nada, así que puede hacerse cuando se pida.
    """
    if nombre not in _RECURSOS:
        _RECURSOS[nombre] = Recurso(nombre)
    return _RECURSOS[nombre]


# ----------------------------------------------------------------------
# FACTURA — no es un CRUD, y por eso no es un Recurso
# ----------------------------------------------------------------------
# La API le da cuatro endpoints: listar, ver una, crearla con su detalle, y
# anularla. No hay PUT, ni PATCH, ni DELETE, y su ausencia es la regla de
# negocio hecha contrato: una factura emitida no se corrige ni desaparece.


def listar_facturas():
    r = _llamar("GET", "/api/factura")
    if r is None:
        return False, [], NO_DISPONIBLE
    if r.status_code == 204:
        return True, [], []
    if r.status_code == 200:
        return True, _cuerpo(r).get("datos", []), []
    return False, [], _mensajes(r)


def obtener_factura(numero):
    r = _llamar("GET", f"/api/factura/{numero}")
    if r is None:
        return False, None, NO_DISPONIBLE
    if r.status_code == 200:
        return True, _cuerpo(r), []
    return False, None, _mensajes(r)


def crear_factura(datos: dict):
    """POST /api/factura → (ok, numero, errores).

    El cuerpo es MAESTRO-DETALLE: el cliente, el vendedor y una lista de
    renglones. La API lo resuelve en una sola transacción y calcula el total
    con un trigger: el front no suma nada.

    OJO con la forma de la respuesta: el número de la factura NO viene en la
    raíz, sino anidado en `factura`, junto con la fecha y el total que calculó
    la base:

        {"estado": 200, "mensaje": "…",
         "factura": {"numero": 8, "total": 800000, …},
         "productos": [ … ]}

    Suponerlo en la raíz es el tipo de error que solo aparece corriendo el
    sistema: la factura se crea bien y el front se cae DESPUÉS, al redirigir.
    """
    r = _llamar("POST", "/api/factura", json=datos)
    if r is None:
        return False, None, NO_DISPONIBLE
    if r.status_code == 200:
        return True, (_cuerpo(r).get("factura") or {}).get("numero"), []
    return False, None, _mensajes(r)


def anular_factura(numero):
    """POST /api/factura/{numero}/anular → (ok, errores).

    Anular NO es borrar: la factura sigue ahí, con estado 'anulada'.
    """
    r = _llamar("POST", f"/api/factura/{numero}/anular")
    if r is None:
        return False, NO_DISPONIBLE
    return (True, []) if r.status_code == 200 else (False, _mensajes(r))


# ----------------------------------------------------------------------
# USUARIO — lo nuevo de la v7
# ----------------------------------------------------------------------
# El front NO comprueba contraseñas: se las manda a la API y acata lo que
# responda. Aquí no hay bcrypt, ni hashes, ni comparaciones: si esa lógica
# estuviera duplicada en el front, habría dos maneras de entrar al sistema
# y solo una estaría auditada.


def verificar_credenciales(email: str, contrasena: str):
    """POST /api/usuario/verificar-contrasena → (ok, datos, mensaje).

    Los tres desenlaces vienen de la API, no de aquí:
        200 → entra, y la respuesta trae sus roles
        401 → credenciales inválidas
        404 → el usuario no existe
    """
    r = _llamar("POST", "/api/usuario/verificar-contrasena",
                json={"email": email, "contrasena": contrasena})
    if r is None:
        return False, None, NO_DISPONIBLE[0]
    if r.status_code == 200:
        return True, _cuerpo(r), ""
    if r.status_code == 401:
        return False, None, "Credenciales inválidas."
    if r.status_code == 404:
        # La API distingue 401 de 404; el front NO se lo cuenta al usuario,
        # porque decir "ese correo no existe" es confirmar cuáles sí.
        return False, None, "Credenciales inválidas."
    if r.status_code == 422:
        return False, None, "; ".join(_mensajes(r))
    return False, None, "No se pudo validar (intente de nuevo)."
