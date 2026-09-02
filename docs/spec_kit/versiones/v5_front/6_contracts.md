# Contratos — Versión 5: las PANTALLAS

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

> En la API el contrato son los endpoints. **En el front, el contrato son las
> pantallas**: qué ruta muestra qué, y a qué endpoint llama cada acción.
> Base: `http://localhost:8023`.

## 0. El mapa completo

| Ruta | Método | Qué hace | A qué llama en la API |
|---|---|---|---|
| `/` | GET | Redirige (302) a `/productos` | — |
| `/productos` | GET | La tabla | `GET /api/producto` |
| `/productos/nuevo` | GET | El formulario vacío | — |
| `/productos/nuevo` | POST | Crea | `POST /api/producto` |
| `/productos/<cod>/editar` | GET | El formulario con los datos | `GET /api/producto/<cod>` |
| `/productos/<cod>/editar` | POST | Reemplaza **o** actualiza | `PUT` **o** `PATCH` |
| `/productos/<cod>/eliminar` | POST | Elimina | `DELETE /api/producto/<cod>` |

**Cuatro pantallas y seis de los 34 endpoints.** Las otras cinco entidades son
este mismo patrón con otros nombres.

## 1. `/productos` — el listado

| La API responde | La pantalla muestra |
|---|---|
| **200** | La tabla, y abajo *"N producto(s)"* |
| **204** | *"No hay productos todavía"*, en gris — **no es un error** |
| No responde | La página **carga igual**, con el aviso rojo *"El servicio no está disponible"* |

## 2. `/productos/nuevo` — crear

Los cuatro campos van como texto, sin conversión.

| Caso | Resultado |
|---|---|
| Todo correcto | **302** al listado + aviso verde |
| Falta un campo | **200**: vuelve el formulario **con lo digitado** y el 422 arriba |
| `stock` = `abc` | **200** con `stock: Input should be a valid integer…` |
| Código repetido | **200** con el 500 de la API: la llave la defiende la base |

## 3. `/productos/<codigo>/editar` — LA PANTALLA DE LA VERSIÓN

Un formulario, **dos botones**:

```html
<button type="submit" name="verbo" value="put">Reemplazar (PUT)</button>
<button type="submit" name="verbo" value="patch">Actualizar lo diligenciado (PATCH)</button>
```

Con **el mismo formulario**, el nombre borrado:

| Botón | Qué viaja | La API responde | La pantalla |
|---|---|---|---|
| **Reemplazar (PUT)** | los tres campos, vacío incluido | **422** `nombre: String should have at least 1 character` | vuelve al formulario con el aviso |
| **Actualizar (PATCH)** | solo `stock` y `valorunitario` | **200** | **302** al listado, guardado |

**Esa es la lección entera**, y se ve sin leer una línea de código: reemplazar
es poner todo de nuevo; actualizar es tocar lo que se diligenció.

**Caso aparte:** PATCH con **todos** los campos vacíos no llega a la API. El
front avisa *"No diligenció ningún campo"* y se queda en la pantalla.

## 4. `/productos/<codigo>/eliminar` — POST, nunca GET

Es un formulario con `confirm()`, no un enlace. **Un GET que borra lo puede
disparar el navegador solo** al precargar la página.

## 5. Los avisos

Todo error de la API acaba en un aviso arriba de la pantalla:

| Origen | Se ve como |
|---|---|
| 422 de Pydantic (lista) | una línea por campo: `campo: explicación` |
| 400 / 404 / 500 (diccionario) | el `mensaje` y el `detalle` de la API |
| Sin respuesta | *"El servicio no está disponible. ¿Está arriba la API?"* |

Los mensajes de Pydantic salen **en inglés**, porque los escribe el framework
y no nosotros. Traducirlos es posible, pero **nadie lo ha pedido**: sería
anticipar (Artículo 1). Queda anotado para la versión que lo necesite.
