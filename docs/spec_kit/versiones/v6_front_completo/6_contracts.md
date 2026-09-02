# Contratos — Versión 6: las pantallas de las seis entidades

> **Versión 6** ([mapa](../0_mapa_versiones.md)) · Rige la
> [constitución](../../1_constitution.md). **Acumulativa:** la API v1–v4 y el
> front de la v5 **no se rompen** — la v6 extiende el front a las seis
> entidades.
>
> | Documento | Contenido |
> |---|---|
> | [2_spec.md](2_spec.md) | QUÉ agrega la v6 y sus criterios |
> | [3_plan.md](3_plan.md) | CÓMO: el front declarativo |
> | [4_research.md](4_research.md) | Las decisiones, con lo que se descartó |
> | [5_data_model.md](5_data_model.md) | El front sigue **sin datos propios** |
> | [6_contracts.md](6_contracts.md) | Las PANTALLAS de las seis entidades |
> | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test |
> | [8_tasks.md](8_tasks.md) | El orden de construcción por fases |
> | [9_checklist.md](9_checklist.md) | La compuerta 3: se firma ANTES de programar |
> | [GUIA_IA6.md](GUIA_IA6.md) | Construirla con ayuda de una IA |

---

> En el front el contrato son **las pantallas**. Base:
> `http://localhost:8023`.

## 0. El mapa

### Las cinco con CRUD — cuatro rutas para todas

| Ruta | Método | Qué hace | En la API |
|---|---|---|---|
| `/<entidad>` | GET | La tabla | `GET /api/<entidad>` |
| `/<entidad>/nuevo` | GET · POST | Formulario · crear | `POST /api/<entidad>` |
| `/<entidad>/<llave>/editar` | GET · POST | Formulario · reemplazar **o** actualizar | `PUT` **o** `PATCH` |
| `/<entidad>/<llave>/eliminar` | POST | Elimina | `DELETE` |

`<entidad>` ∈ `producto` · `persona` · `empresa` · `cliente` · `vendedor`.
Cualquier otra cosa responde **404**.

### Factura — tres rutas propias

| Ruta | Método | Qué hace | En la API |
|---|---|---|---|
| `/facturas` | GET | La lista | `GET /api/factura` |
| `/facturas/nueva` | GET · POST | Formulario maestro-detalle · crear | `POST /api/factura` |
| `/facturas/<numero>` | GET | El detalle | `GET /api/factura/{numero}` |
| `/facturas/<numero>/anular` | POST | Anula | `POST /api/factura/{numero}/anular` |

**No hay `/facturas/<n>/editar` ni `/facturas/<n>/eliminar`**, y su ausencia
es parte del contrato: responden **404**.

## 1. El formulario de una entidad sin llaves foráneas

Todos los campos son `<input type="text">`, incluidos los numéricos. Con
`type="number"` el navegador rechazaría `abc` antes de enviarlo y **el 422 de
la API no se vería nunca**.

| Caso | Resultado |
|---|---|
| Correcto | **302** al listado + aviso verde |
| Falta un campo | **200**: vuelve el formulario **con lo digitado** y el 422 |
| `stock` = `abc` | `stock: Input should be a valid integer…` |
| Llave repetida | el 500 de la API: la llave la defiende la base |

## 2. El formulario de una entidad CON llaves foráneas

```html
<select name="fkcodpersona">
  <option value="">— elija —</option>
  <option value="P001">P001 — Ana Torres</option>
  …
</select>
```

- Las opciones vienen de `GET /api/persona`: **otra llamada HTTP**, no una
  consulta a la base.
- Si el catálogo está vacío, la pantalla dice *"No hay personas todavía: cree
  una primero"*.
- **La llave generada no aparece** al crear. Al editar se muestra sin poder
  cambiarse.
- **El opcional en blanco no se envía**, y el registro queda con `null`.

| Caso | Resultado |
|---|---|
| `credito` = `mucho` | `credito: Input should be a valid decimal` |
| `fkcodempresa` vacío | se **omite** del cuerpo → `fkcodempresa: null` |

## 3. La pareja PUT/PATCH — ahora en las cinco

Sigue siendo el mismo formulario con dos botones:

| Botón | Qué viaja | Con un campo en blanco |
|---|---|---|
| **Reemplazar (PUT)** | todos los campos, vacíos incluidos | **422** |
| **Actualizar (PATCH)** | solo los diligenciados | **200** |

Con todos los campos vacíos, PATCH **no llama a la API**: avisa y se queda.

## 4. Las pantallas de factura

### `/facturas` — la lista
Número, fecha, cliente, vendedor, total y **estado**. Las anuladas se ven
atenuadas, **pero siguen ahí**. Solo hay un botón: **Ver**.

### `/facturas/nueva` — maestro y detalle
- El **maestro**: dos `<select>`, cliente y vendedor.
- El **detalle**: cinco filas de `<select>` producto + cantidad. Se envían
  como listas paralelas; los renglones incompletos se descartan.
- **Sin ningún renglón**, el front avisa y **no llama a la API**.
- Al crear, la respuesta trae el número **anidado**:
  `{"factura": {"numero": 8, …}, "productos": […]}` — no en la raíz.

### `/facturas/<numero>` — el detalle
El maestro en una ficha y los renglones en una tabla con su subtotal y el
total al pie. **Ese total lo calculó un trigger**, no la pantalla.

### `/facturas/<numero>/anular`
Cambia el estado a `anulada`. **La factura sigue existiendo con su detalle
completo.** No hay ninguna ruta que la borre.

## 5. Los avisos

| Origen | Se ve como |
|---|---|
| 422 de Pydantic (lista) | una línea por campo: `campo: explicación` |
| 400 / 404 / 500 (diccionario) | el `mensaje` y el `detalle` de la API |
| Sin respuesta | *"El servicio no está disponible. ¿Está arriba la API?"* |

Los mensajes de Pydantic salen **en inglés** porque los escribe el framework.
Traducirlos no lo ha pedido nadie: sería anticipar (Artículo 1).
