"""
app.py — La capa de PRESENTACIÓN del sistema.

Las tres reglas siguen siendo las de la v5:

1. **No habla con la base de datos.** Ni sabe que existen tres motores.
2. **No valida negocio.** Si un crédito negativo está mal, lo dice la API con
   un 422 y aquí solo se muestra.
3. **No arma SQL.**

**Lo que cambió en la v7.** El sistema pide identificarse. Toda ruta exige
sesión, y el menú se dibuja según los roles de quien entró. Pero ojo con lo
que eso NO es: **el front no protege nada**. Sigue sin decidir; solo dibuja.
Quien decide si unas credenciales sirven es la API, y quien podría negar el
acceso a un dato también — cuando la tenga (ver 4_research §D3).

**Lo que cambió en la v6.** Cinco entidades comparten el mismo CRUD, así que
comparten las mismas cuatro rutas: `<entidad>` sale de la URL y se busca en
`entidades.py`. Escribir cinco veces las mismas vistas habría dado cinco
sitios donde arreglar el mismo error.

`factura` tiene rutas propias porque **no es un CRUD**: se crea con su detalle
y se anula. Meterla a la fuerza en el patrón genérico sería inventarle a la
API endpoints que no tiene.
"""

import os

from functools import wraps

from flask import (Flask, abort, flash, redirect, render_template, request,
                   session, url_for)

import cliente_api
from entidades import ENTIDADES, visibles_para

app = Flask(__name__)
app.secret_key = os.environ.get("CLAVE_SESION", "Paradigmas123!Sesion")
PUERTO = int(os.environ.get("PUERTO", 8023))


@app.context_processor
def _menu():
    """El menú sale de la misma declaración, no de una lista escrita aparte
    que habría que acordarse de actualizar.

    Desde la v7 se filtra por los roles de quien entró: un vendedor no ve
    Usuarios. **Eso es lo que se dibuja, no lo que se permite.**
    """
    return {"entidades": visibles_para(session.get("roles")),
            "usuario": session.get("email"),
            "roles": session.get("roles", [])}


def exige_sesion(vista):
    """Toda ruta pasa por aquí, menos el login y el logout.

    Es un decorador y no un `if` copiado en cada vista, porque una ruta a la
    que se le olvide el `if` queda abierta **sin que nadie lo note**. Así,
    olvidarse es imposible: o la vista está decorada, o no existe.
    """
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "email" not in session:
            flash("Entre al sistema para continuar.", "error")
            return redirect(url_for("login"))
        return vista(*args, **kwargs)
    return envoltura


def _entidad(nombre: str):
    """La declaración de la entidad, o 404 si la URL nombra una que no existe."""
    definicion = ENTIDADES.get(nombre)
    if definicion is None:
        abort(404)
    return definicion


def _avisar(errores: list[str]) -> None:
    for mensaje in errores:
        flash(mensaje, "error")


def _opciones(definicion):
    """Las listas de las que se ELIGEN las llaves foráneas.

    Un cliente no digita el código de su persona: lo escoge de las que existen.
    Esas opciones se piden a la API —otra vez, por HTTP— porque el front no
    tiene de dónde más sacarlas.
    """
    listas = {}
    for campo in definicion.campos:
        if campo.opciones_de:
            ok, filas, _ = cliente_api.recurso(campo.opciones_de).listar()
            listas[campo.nombre] = filas if ok else []
    return listas


# ======================================================================
# LA SESIÓN — lo nuevo de la v7
# ======================================================================


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", email=None)

    email = request.form.get("email", "").strip()
    contrasena = request.form.get("contrasena", "")

    # El front NO comprueba la contraseña: se la manda a la API.
    ok, datos, mensaje = cliente_api.verificar_credenciales(email, contrasena)

    if not ok:
        flash(mensaje, "error")
        # Se devuelve el correo, no la contraseña: repetir un correo largo
        # es una molestia evitable; repetir una contraseña en pantalla, no.
        return render_template("login.html", email=email)

    # La sesión guarda el correo y los ROLES que devolvió la API. Nada más:
    # ningún dato de negocio, y por supuesto ninguna contraseña.
    session["email"] = datos.get("email", email)
    session["roles"] = datos.get("roles", [])

    roles = ", ".join(session["roles"]) or "sin roles asignados"
    flash(f"Bienvenido, {session['email']} ({roles}).", "exito")
    return redirect(url_for("inicio"))


@app.route("/logout")
def logout():
    session.clear()
    flash("Salió del sistema.", "exito")
    return redirect(url_for("login"))


# ======================================================================
# Las cinco entidades con CRUD: UNAS rutas para todas
# ======================================================================


@app.route("/")
@exige_sesion
def inicio():
    return redirect(url_for("listar", entidad="producto"))


@app.route("/<entidad>")
@exige_sesion
def listar(entidad):
    definicion = _entidad(entidad)
    ok, filas, errores = cliente_api.recurso(entidad).listar()
    if not ok:
        _avisar(errores)
    # Aun con error se renderiza: el usuario ve el aviso DENTRO de la
    # aplicación, no una pantalla de excepción de Flask.
    return render_template("entidades/lista.html", d=definicion, filas=filas)


@app.route("/<entidad>/nuevo", methods=["GET", "POST"])
@exige_sesion
def crear(entidad):
    definicion = _entidad(entidad)

    if request.method == "GET":
        return render_template("entidades/formulario.html", d=definicion,
                               registro=None, opciones=_opciones(definicion))

    # Los valores viajan COMO TEXTO, tal como llegaron del formulario.
    # Convertirlos aquí sería adelantarse a la validación de la API: si el
    # stock dice "abc", que lo rechace ella con un 422 — así se ve la frontera.
    datos = {c.nombre: request.form.get(c.nombre, "").strip()
             for c in definicion.campos}
    # Un opcional en blanco NO se envía: enviarlo vacío es decir "ponlo en
    # cadena vacía", que no es lo mismo que "no lo tiene".
    datos = {k: v for k, v in datos.items()
             if v != "" or _es_obligatorio(definicion, k)}

    ok, errores = cliente_api.recurso(entidad).crear(datos)
    if ok:
        flash(f"Se creó {definicion.singular}.", "exito")
        return redirect(url_for("listar", entidad=entidad))

    _avisar(errores)
    # Vuelve el formulario CON lo digitado: perderlo por un error de
    # validación es castigar al usuario dos veces.
    return render_template("entidades/formulario.html", d=definicion,
                           registro=datos, opciones=_opciones(definicion))


def _es_obligatorio(definicion, nombre: str) -> bool:
    return any(c.nombre == nombre and c.obligatorio for c in definicion.campos)


@app.route("/<entidad>/<llave>/editar", methods=["GET", "POST"])
@exige_sesion
def editar(entidad, llave):
    definicion = _entidad(entidad)
    recurso = cliente_api.recurso(entidad)

    if request.method == "GET":
        ok, registro, errores = recurso.obtener(llave)
        if not ok:
            _avisar(errores)
            return redirect(url_for("listar", entidad=entidad))
        return render_template("entidades/formulario.html", d=definicion,
                               registro=registro, opciones=_opciones(definicion))

    # Qué botón se oprimió decide el verbo. La diferencia NO es un if de
    # negocio: es QUÉ SE ENVÍA.
    verbo = request.form.get("verbo", "patch")
    campos = {c.nombre: request.form.get(c.nombre, "").strip()
              for c in definicion.campos_editables}

    if verbo == "put":
        # PUT: reemplazo COMPLETO. Los campos viajan aunque estén vacíos, y
        # por eso uno en blanco responde 422. Esa es la semántica de PUT.
        ok, errores = recurso.reemplazar(llave, campos)
        hecho = "reemplazó (PUT)"
    else:
        # PATCH: viaja SOLO lo diligenciado. El mismo formulario a medio
        # llenar que el PUT rechaza, aquí funciona.
        parciales = {k: v for k, v in campos.items() if v != ""}
        if not parciales:
            flash("No diligenció ningún campo: no hay nada que actualizar.", "error")
            return redirect(url_for("editar", entidad=entidad, llave=llave))
        ok, errores = recurso.actualizar(llave, parciales)
        hecho = "actualizó (PATCH)"

    if ok:
        flash(f"Se {hecho} {definicion.singular}.", "exito")
        return redirect(url_for("listar", entidad=entidad))

    _avisar(errores)
    return render_template("entidades/formulario.html", d=definicion,
                           registro={definicion.llave: llave, **campos},
                           opciones=_opciones(definicion))


@app.route("/<entidad>/<llave>/eliminar", methods=["POST"])
@exige_sesion
def eliminar(entidad, llave):
    # POST y no un enlace: un GET que borra lo puede disparar el navegador
    # solo al precargar la página.
    definicion = _entidad(entidad)
    ok, errores = cliente_api.recurso(entidad).eliminar(llave)
    if ok:
        flash(f"Se eliminó {definicion.singular}.", "exito")
    else:
        _avisar(errores)
    return redirect(url_for("listar", entidad=entidad))


# ======================================================================
# FACTURA — rutas propias, porque no es un CRUD
# ======================================================================


@app.route("/facturas")
@exige_sesion
def facturas():
    ok, filas, errores = cliente_api.listar_facturas()
    if not ok:
        _avisar(errores)
    return render_template("facturas/lista.html", facturas=filas)


@app.route("/facturas/<numero>")
@exige_sesion
def factura(numero):
    ok, doc, errores = cliente_api.obtener_factura(numero)
    if not ok:
        _avisar(errores)
        return redirect(url_for("facturas"))
    return render_template("facturas/detalle.html", f=doc)


@app.route("/facturas/nueva", methods=["GET", "POST"])
@exige_sesion
def nueva_factura():
    # El maestro y el detalle se arman con lo que YA existe: no se digita un
    # código de cliente ni de producto, se eligen.
    def _catalogos():
        return {
            "clientes": cliente_api.recurso("cliente").listar()[1],
            "vendedores": cliente_api.recurso("vendedor").listar()[1],
            "productos": cliente_api.recurso("producto").listar()[1],
        }

    if request.method == "GET":
        return render_template("facturas/nueva.html", **_catalogos())

    # El detalle llega como listas paralelas: producto[i] con cantidad[i].
    # Solo entran los renglones con producto elegido Y cantidad diligenciada.
    codigos = request.form.getlist("codigo")
    cantidades = request.form.getlist("cantidad")
    renglones = [{"codigo": c, "cantidad": n}
                 for c, n in zip(codigos, cantidades) if c and n]

    if not renglones:
        flash("Una factura necesita al menos un producto.", "error")
        return render_template("facturas/nueva.html", **_catalogos())

    datos = {
        "fkidcliente": request.form.get("fkidcliente", ""),
        "fkidvendedor": request.form.get("fkidvendedor", ""),
        "productos": renglones,
    }

    ok, numero, errores = cliente_api.crear_factura(datos)
    if ok:
        # El total NO lo calculó el front: lo calculó un trigger en la base.
        flash(f"Se creó la factura {numero}.", "exito")
        if numero is None:
            # Se creó, pero la respuesta no trajo el número. Se va al listado
            # en vez de armar una URL con None: el usuario NO puede terminar
            # en una pantalla de error por algo que sí funcionó.
            return redirect(url_for("facturas"))
        return redirect(url_for("factura", numero=numero))

    _avisar(errores)
    return render_template("facturas/nueva.html", **_catalogos())


@app.route("/facturas/<numero>/anular", methods=["POST"])
@exige_sesion
def anular(numero):
    # No existe 'eliminar factura': la API no da DELETE, y esa ausencia es la
    # regla contable hecha contrato.
    ok, errores = cliente_api.anular_factura(numero)
    if ok:
        flash(f"La factura {numero} quedó ANULADA. No se borró: sigue ahí.", "exito")
    else:
        _avisar(errores)
    return redirect(url_for("factura", numero=numero))


if __name__ == "__main__":
    # host 0.0.0.0: dentro del contenedor hay que escuchar en todas las
    # interfaces, o el puerto publicado no llega a ninguna parte.
    app.run(host="0.0.0.0", port=PUERTO, debug=True)
