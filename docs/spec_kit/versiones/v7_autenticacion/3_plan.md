# Plan — Versión 7: dónde vive cada pieza

> **Versión 7** ([mapa](../0_mapa_versiones.md)) · Rige la
> [constitución](../../1_constitution.md). **La primera versión que TOCA LA
> API** desde que nació el front: hasta la v6 solo se le agregaban clientes;
> aquí la API estrena una entidad.
>
> | Documento | Contenido |
> |---|---|
> | [2_spec.md](2_spec.md) | QUÉ agrega la v7 y sus criterios |
> | [3_plan.md](3_plan.md) | CÓMO: dónde vive cada pieza de la autenticación |
> | [4_research.md](4_research.md) | Las decisiones, con lo que se descartó |
> | [5_data_model.md](5_data_model.md) | Las tablas que llevaban 6 versiones dormidas |
> | [6_contracts.md](6_contracts.md) | Los endpoints y las pantallas |
> | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test |
> | [8_tasks.md](8_tasks.md) | El orden de construcción por fases |
> | [9_checklist.md](9_checklist.md) | La compuerta 3: se firma ANTES de programar |
> | [GUIA_IA7.md](GUIA_IA7.md) | Construirla con ayuda de una IA |

---

## 1. Lo que se agrega

```
api_facturas/
├── models/usuario.py                      Usuario · Reemplazo · Actualizar · Credenciales
├── repositorios/
│   ├── abstracciones/i_repositorio_usuario.py
│   ├── repositorio_usuario_postgresql.py  ┐
│   ├── repositorio_usuario_mariadb.py     ├ los TRES motores
│   └── repositorio_usuario_sqlserver.py   ┘
├── servicios/
│   ├── abstracciones/i_servicio_usuario.py
│   └── servicio_usuario.py                ← bcrypt vive AQUÍ
└── controllers/usuario_controller.py

front_flask/
├── templates/login.html                   la única pantalla sin sesión
├── app.py                                 + /login, /logout, @exige_sesion
├── entidades.py                           + USUARIO y el filtro por roles
└── cliente_api.py                         + verificar_credenciales()
```

## 2. La pregunta que ordena la versión: ¿dónde va bcrypt?

Podía ir en tres sitios, y solo uno es correcto:

| Si fuera… | Qué pasaría |
|---|---|
| En el **controller** | La capa que solo debe traducir HTTP sabría de criptografía. Y habría que repetirlo en cada endpoint que toque contraseñas |
| En el **repositorio** | Habría que escribirlo **tres veces**, una por motor — y son tres copias de una regla que no depende del motor |
| En el **servicio** ✅ | Se escribe **una vez**, los tres motores la heredan, y las otras dos capas siguen sin enterarse |

Que la respuesta caiga sola es la señal de que las capas estaban bien
puestas desde la v1. **La prueba de una arquitectura no es que se vea bonita
en un diagrama: es que cuando llega un requisito nuevo, su sitio sea
obvio.**

## 3. Las piezas, una por una

### 3.1 `obtener_hash` está aparte, y a propósito

El repositorio tiene `obtener_por_email` (que **no** trae la contraseña) y
`obtener_hash` (que trae **solo** eso). Son dos porque así **la única
consulta que saca esa columna es la que la necesita**. Si el listado la
trajera "por si acaso", algún día saldría impresa en una respuesta.

### 3.2 El servicio distingue "no existe" de "no coincide"

`LookupError` y `PermissionError` son excepciones distintas, y el controller
las traduce a 404 y 401. **Que la API los distinga es correcto**: quien
administra necesita saber cuál fue. Lo que no corresponde es contárselo a
quien está tocando la puerta — y por eso **el front los aplana a un solo
mensaje** (RF5). La distinción se pierde **en la capa que habla con el
usuario**, no en la que sabe la verdad.

### 3.3 El decorador, no el `if`

```python
@app.route("/<entidad>")
@exige_sesion
def listar(entidad):
```

Nueve rutas lo llevan. Con un `if` copiado en cada vista, la ruta a la que se
le olvide **queda abierta y nadie se entera**. Con el decorador, o está
puesto o la vista no compila en la cabeza de quien la lee.

### 3.4 La sesión guarda dos cosas: correo y roles

Nada de negocio, ninguna contraseña. Va firmada con `CLAVE_SESION`.

## 4. Un error de esta versión, y por qué se cuenta

Al agregar `usuario` a `entidades.py`, la pantalla respondía **500**. La causa:
`cliente_api` tenía **una segunda lista** de entidades escrita a mano, y se
agregó en una sola de las dos.

**La corrección no fue agregar la que faltaba.** Eso deja la trampa puesta
para la próxima entidad. Se quitó la segunda lista: ahora los recursos se
crean cuando se piden.

> Es la misma lección de la v6, cobrada en carne propia: **dos listas que
> deben coincidir siempre terminan no coincidiendo.** Y la señal fue justo la
> que enseña el método: el menú mostraba algo que la pantalla no podía servir
> — **el documento decía una cosa y el sistema hacía otra**.

## 5. Chequeo de constitución

| Artículo | ¿Se respeta? | Cómo |
|---|---|---|
| 1 — No anticipar | ✅ | Sin JWT, sin permisos, sin registro público |
| 2 — SQL a la vista y parametrizado | ✅ | El SQL de usuario se ve, y el email siempre va como `:email` |
| 3 — Capas con interfaces | ✅ | **Y la versión lo pone a prueba**: bcrypt cae solo en el servicio |
| 4 — Un solo comando | ✅ | Sigue siendo `up -d --build` |
| 5 — La base es dada | ✅ | Las cinco tablas ya existían desde la v1: **no se creó ninguna** |
| 6 — Los contratos al pie de la letra | ✅ | Los cuatro desenlaces de verificar están escritos y probados |
| 7 — Secretos | ⚠️ **Con una nota** | `CLAVE_SESION` va en el compose, como la excepción declarada. **Pero las contraseñas de los usuarios ya NO están en claro**: van cifradas, y esa parte deja de ser didáctica |
| 8 — Todo en español | ✅ | Salvo los mensajes de Pydantic, que los escribe el framework |

**Ningún artículo obliga a cambiar el plan.** La compuerta pasa.
