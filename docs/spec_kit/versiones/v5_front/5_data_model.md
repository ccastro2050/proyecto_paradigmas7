# Modelo de datos — Versión 5: el front no tiene datos

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

## 1. El front no tiene modelo de datos, y eso es el punto

No hay tablas nuevas. No hay migraciones. **No hay una sola línea de SQL en
`front_flask/`**, y no la hay porque el front no tiene por dónde escribirla:
su contenedor no recibe ninguna cadena de conexión.

Lo único que el front conoce del mundo exterior es una variable:

```yaml
API_FACTURAS_URL: http://api-facturas:8021
```

Compare esa línea con lo que recibe la API, que sí tiene tres cadenas de
conexión y un interruptor de motor. **Esa diferencia ES la arquitectura**, y
está declarada en el `docker-compose.yml` donde cualquiera puede verla.

## 2. La forma del producto, que el front recibe pero no define

| Campo | Tipo | Quién manda |
|---|---|---|
| `codigo` | texto (1–20) | La API. Es la llave |
| `nombre` | texto (≥ 1) | La API |
| `stock` | entero ≥ 0 | La API |
| `valorunitario` | decimal ≥ 0 | La API |

El front **muestra** estos campos y los **reenvía** como texto. No los
convierte, no los redondea y no los valida: si el `stock` llega como `"abc"`,
viaja `"abc"` y la API responde 422 (ver [D2](4_research.md)).

## 3. Lo único que el front sí guarda

La **sesión de Flask**, y solo para los avisos de `flash()` —el mensaje verde
de "producto creado" que sobrevive a la redirección—. Va firmada con
`CLAVE_SESION`, vive en una cookie del navegador y **no contiene datos del
negocio**.

## 4. Invariantes

1. `front_flask/` no importa ningún driver de base de datos.
2. `front_flask/` no recibe ninguna cadena de conexión.
3. Todo dato que se muestra vino de una respuesta HTTP de la API.
4. Si la API está caída, **no hay datos** — comprobable con el criterio 7.
