# Modelo de datos — Versión 6: el front sigue sin datos

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

## 1. Sigue sin tener modelo de datos

Como en la v5: **ninguna tabla, ninguna migración, ni una línea de SQL** en
`front_flask/`. Su contenedor no recibe cadenas de conexión y no importa
drivers. Lo único que conoce del exterior:

```yaml
API_FACTURAS_URL: http://api-facturas:8021
```

## 2. Entonces, ¿qué es `entidades.py`?

Es la pregunta que hay que hacerse, porque **parece** un modelo de datos y no
lo es.

| `entidades.py` **sí** | `entidades.py` **no** |
|---|---|
| Describe qué campos tiene un formulario | Define qué campos existen |
| Dice cuál campo es una llave foránea | Impone la integridad referencial |
| Dice si una llave se digita | Genera la llave |
| Pone etiquetas en español | Valida nada |

**Todo lo de la derecha vive en la API y en la base.** Si `entidades.py`
dijera que `credito` es obligatorio y el modelo Pydantic dijera que no, **la
que manda es la API**: este archivo estaría mal y habría que corregirlo.

Es una **descripción de presentación**, no una fuente de verdad.

## 3. La forma de cada entidad, según la API

| Entidad | Llave | ¿Se digita? | Campos |
|---|---|---|---|
| `producto` | `codigo` | sí | nombre · stock · valorunitario |
| `persona` | `codigo` | sí | nombre · email · telefono |
| `empresa` | `codigo` | sí | nombre |
| `cliente` | `id` | **no**, la genera la base | credito · **fkcodpersona** · **fkcodempresa** (opcional) |
| `vendedor` | `id` | **no**, la genera la base | carnet · direccion · **fkcodpersona** |
| `factura` | `numero` | **no** | fkidcliente · fkidvendedor · **productos[]** |

## 4. La factura llega armada

`GET /api/factura/<numero>` devuelve el maestro **y su detalle en una sola
respuesta**, con los nombres del cliente y del vendedor ya resueltos y el
subtotal de cada renglón:

```json
{"numero": 1, "fecha": "…", "total": 5000000, "estado": "activa",
 "fkidcliente": 1, "nombre_cliente": "Ana Torres",
 "fkidvendedor": 1, "nombre_vendedor": "Carlos Pérez",
 "productos": [{"codigo_producto": "PR001", "nombre_producto": "…",
                "cantidad": 2, "valorunitario": 2500000, "subtotal": 5000000}]}
```

**El front no cruzó nada.** No pidió el cliente aparte para saber su nombre,
ni multiplicó cantidad por valor. El join y las sumas los hizo quien tiene los
datos.

## 5. Invariantes

1. `front_flask/` no importa ningún driver de base de datos.
2. No recibe ninguna cadena de conexión.
3. Todo dato mostrado vino de una respuesta HTTP.
4. `entidades.py` no contradice a los modelos de la API.
5. Si la API está caída, **no hay datos en ninguna de las seis pantallas**.
