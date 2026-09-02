# Investigación — Versión 5: las decisiones y lo que se descartó

> **Versión 5** ([mapa](../0_mapa_versiones.md)) · Rige la
> [constitución](../../1_constitution.md). **Acumulativa:** la API v1–v4
> (tri-motor, 34 endpoints) **NO se toca** — la v5 le pone encima su primer
> cliente visual.
>
> | Documento | Contenido |
> |---|---|
> | [2_spec.md](2_spec.md) | QUÉ agrega la v5 y sus criterios |
> | [3_plan.md](3_plan.md) | CÓMO: la arquitectura del front |
> | [4_research.md](4_research.md) | Las decisiones, con lo que se descartó |
> | [5_data_model.md](5_data_model.md) | El front **no tiene datos propios** |
> | [6_contracts.md](6_contracts.md) | Las PANTALLAS: el contrato del front |
> | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test |
> | [8_tasks.md](8_tasks.md) | El orden de construcción por fases |
> | [9_checklist.md](9_checklist.md) | La compuerta 3: se firma ANTES de programar |
> | [GUIA_IA5.md](GUIA_IA5.md) | Construirla con ayuda de una IA |

---

## D1 — Flask + Jinja2, renderizado en el servidor

**Alternativas:** React/Vue con la API como backend · Streamlit · Django.

**Se eligió Flask con plantillas** porque la versión enseña **la separación
entre front y API**, y un framework de JavaScript metería, antes de esa
lección, un empaquetador, un `node_modules` y un modelo de estado en el
navegador. Con Jinja2 el front cabe en dos archivos de Python y el
tema del día se ve sin ruido alrededor.

**Lo que se pierde y se acepta:** cada acción recarga la página. Para un CRUD
es perfectamente usable, y a cambio no hay una sola línea de JavaScript que
explicar.

## D2 — El front NO valida

**Alternativa:** repetir en el formulario las reglas de Pydantic —campos
obligatorios, `stock >= 0`— para "ahorrarle un viaje al servidor".

**Se descartó.** Esa regla ya tiene dueño: los modelos de la API. Copiarla
aquí crea dos fuentes de la misma verdad, y el día que una cambie sin la otra,
el sistema miente en una de las dos pantallas.

**La consecuencia se ve:** los campos numéricos son `type="text"`. Con
`type="number"`, el navegador rechazaría `abc` antes de enviarlo y **el 422 no
se vería nunca**. Se prefiere que el estudiante vea dónde está la frontera
real de la validación.

## D3 — `cliente_api.py` separado de `app.py`

**Alternativa:** llamar a `requests` directamente desde cada vista.

**Se descartó** porque repartiría el conocimiento de "dónde viven los datos"
por todas las vistas. Concentrado en un archivo, cambiar la URL de la API, el
timeout o el manejo de errores se hace **en un solo lugar** — que es lo mismo
que hace el repositorio en el back.

## D4 — Sin login, y por un hecho, no por gusto

**Alternativa:** copiar el login del front de otro proyecto del curso, que
valida contra `POST /api/usuario/verificar-contrasena`.

**Se descartó porque ese endpoint aquí no existe.** La API de la v4 expone
seis controladores —cliente, empresa, factura, persona, producto, vendedor— y
ninguno de `usuario`, aunque la tabla esté en la base desde la v1.

Ponerle login al front obligaría a **abrir un endpoint nuevo en la API**, y la
regla 3 del mapa lo prohíbe: *"el código de una versión no anticipa a la
siguiente"*. La v5 es del front; si el sistema necesita autenticación, esa es
**una versión propia**, con su spec y su decisión, no un pedazo colgado de
esta.

> **Esto es el método funcionando.** Copiar el front de otro proyecto habría
> parecido más rápido y habría fallado en la primera pantalla. Lo que lo
> impidió no fue la suerte: fue mirar los seis controladores **antes** de
> escribir código.

## D5 — Un contenedor aparte para el front

**Alternativa:** servir las plantillas desde el mismo proceso de FastAPI.

**Se descartó** porque volvería a meter en un solo proceso lo que la versión
quiere separar. Con dos imágenes, el criterio 7 se puede ejecutar de verdad:
apagar la API y comprobar que el front sigue en pie **y sin datos**.

## D6 — CSS a mano, sin framework

40 líneas de CSS contra una dependencia más que explicar. Para cuatro
pantallas, la balanza es clara.
