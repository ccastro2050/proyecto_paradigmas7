"""
entidades.py — QUÉ tiene cada entidad, declarado en un solo lugar.

La v5 tenía una entidad y cuatro pantallas escritas a mano. La v6 tiene seis.
Copiar esas cuatro pantallas cinco veces daría treinta plantillas casi
idénticas: el día que haya que cambiar cómo se ve un error, hay que cambiarlo
en treinta sitios y olvidarse de dos.

Así que aquí se DECLARA cada entidad —sus campos, sus etiquetas, cuáles son
llaves foráneas— y `app.py` recorre esa declaración. Agregar una entidad nueva
es agregar un objeto a este archivo, no escribir pantallas.

Esto NO es una regla de negocio: es la forma de los datos que la API ya
declaró en sus modelos Pydantic. Si aquí dijera algo distinto de lo que dice
la API, la que manda es la API — y este archivo estaría mal.
"""

from dataclasses import dataclass, field


@dataclass
class Campo:
    """Un campo del formulario."""

    nombre: str                      # el nombre exacto que espera la API
    etiqueta: str                    # lo que lee el usuario
    obligatorio: bool = True         # solo para redactar la ayuda, NO se valida
    opciones_de: str | None = None   # si es llave foránea: de qué entidad
    ayuda: str = ""


@dataclass
class Entidad:
    """Una entidad con CRUD completo en la API."""

    nombre: str                # 'producto': la ruta de la API y del front
    titulo: str                # 'Productos': el encabezado
    singular: str              # 'el producto': para los avisos
    llave: str                 # cómo se llama la llave EN LA RESPUESTA
    llave_en_ruta: str         # cómo la nombra la URL de la API
    llave_se_digita: bool      # ¿el usuario la escribe al crear?
    campos: list[Campo]
    columnas: list[tuple[str, str]] = field(default_factory=list)
    # v7 — qué roles pueden ver esta entidad. Vacío = todos los que
    # tengan sesión. NO es una regla de seguridad: es lo que se DIBUJA.
    # Ver 4_research §D3: esconder un menú no protege nada.
    roles: tuple[str, ...] = ()

    @property
    def campos_editables(self) -> list[Campo]:
        """Los campos del formulario de edición: la llave nunca se cambia."""
        return [c for c in self.campos if c.nombre != self.llave]


PRODUCTO = Entidad(
    nombre="producto", titulo="Productos", singular="el producto",
    llave="codigo", llave_en_ruta="codigo", llave_se_digita=True,
    campos=[
        Campo("codigo", "Código", ayuda="Hasta 20 caracteres. Es la llave."),
        Campo("nombre", "Nombre"),
        Campo("stock", "Stock", ayuda="Un entero mayor o igual a 0."),
        Campo("valorunitario", "Valor unitario", ayuda="Un número mayor o igual a 0."),
    ],
    columnas=[("codigo", "Código"), ("nombre", "Nombre"),
              ("stock", "Stock"), ("valorunitario", "Valor unitario")],
)

PERSONA = Entidad(
    nombre="persona", titulo="Personas", singular="la persona",
    llave="codigo", llave_en_ruta="codigo", llave_se_digita=True,
    campos=[
        Campo("codigo", "Código", ayuda="Hasta 10 caracteres. Es la llave."),
        Campo("nombre", "Nombre"),
        Campo("email", "Correo"),
        Campo("telefono", "Teléfono"),
    ],
    columnas=[("codigo", "Código"), ("nombre", "Nombre"),
              ("email", "Correo"), ("telefono", "Teléfono")],
)

EMPRESA = Entidad(
    nombre="empresa", titulo="Empresas", singular="la empresa",
    llave="codigo", llave_en_ruta="codigo", llave_se_digita=True,
    campos=[
        Campo("codigo", "Código", ayuda="Hasta 10 caracteres. Es la llave."),
        Campo("nombre", "Nombre"),
    ],
    columnas=[("codigo", "Código"), ("nombre", "Nombre")],
)

# --- Las dos con llaves foráneas -------------------------------------------
# Su llave la genera la base de datos, así que NO se digita al crear: en el
# formulario de creación no aparece.

CLIENTE = Entidad(
    nombre="cliente", titulo="Clientes", singular="el cliente",
    llave="id", llave_en_ruta="id_cliente", llave_se_digita=False,
    campos=[
        Campo("fkcodpersona", "Persona", opciones_de="persona",
              ayuda="Se ELIGE de las personas que existen: es una llave foránea."),
        Campo("credito", "Crédito", ayuda="Un número mayor o igual a 0."),
        Campo("fkcodempresa", "Empresa", obligatorio=False, opciones_de="empresa",
              ayuda="Opcional: un cliente puede no pertenecer a ninguna empresa."),
    ],
    columnas=[("id", "Id"), ("fkcodpersona", "Persona"),
              ("credito", "Crédito"), ("fkcodempresa", "Empresa")],
)

VENDEDOR = Entidad(
    nombre="vendedor", titulo="Vendedores", singular="el vendedor",
    llave="id", llave_en_ruta="id_vendedor", llave_se_digita=False,
    campos=[
        Campo("carnet", "Carnet", ayuda="Un entero mayor o igual a 0."),
        Campo("direccion", "Dirección"),
        Campo("fkcodpersona", "Persona", opciones_de="persona",
              ayuda="Se ELIGE de las personas que existen: es una llave foránea."),
    ],
    columnas=[("id", "Id"), ("carnet", "Carnet"),
              ("direccion", "Dirección"), ("fkcodpersona", "Persona")],
    roles=("Administrador",),
)

# v7 — la entidad que la API estrenó en esta versión. Solo el administrador
# la ve en el menú: los demás no tienen nada que hacer ahí.
USUARIO = Entidad(
    nombre="usuario", titulo="Usuarios", singular="el usuario",
    llave="email", llave_en_ruta="email", llave_se_digita=True,
    campos=[
        Campo("email", "Correo", ayuda="Es la llave: identifica al usuario."),
        Campo("contrasena", "Contraseña",
              ayuda="Se guarda CIFRADA. La API nunca la devuelve, "
                    "así que al editar aparece en blanco."),
    ],
    # La contraseña NO se lista: lo que no se muestra, no se filtra.
    columnas=[("email", "Correo")],
    roles=("Administrador",),
)

# El orden del menú. `factura` NO está aquí: no es un CRUD y tiene sus propias
# pantallas (ver app.py y 2_spec.md §3).
ENTIDADES = {e.nombre: e for e in
             (PRODUCTO, PERSONA, EMPRESA, CLIENTE, VENDEDOR, USUARIO)}


def visibles_para(roles_del_usuario) -> list[Entidad]:
    """Las entidades que se le DIBUJAN a quien tiene esos roles.

    Insisto en «dibujan»: esto arma el menú, no defiende nada. Si alguien
    escribe la URL a mano, la ve igual — y así debe ser hasta que la API
    tenga permisos de verdad (ver 4_research §D3).
    """
    roles = set(roles_del_usuario or ())
    return [e for e in ENTIDADES.values()
            if not e.roles or roles.intersection(e.roles)]
