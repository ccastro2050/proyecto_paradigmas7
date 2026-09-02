# Tareas — Versión 5: el orden de construcción

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

> Cada fase termina en algo **que se puede comprobar**. No se pasa a la
> siguiente sin verificar la anterior.

## Fase 1 — El esqueleto del front

- [ ] `front_flask/` con `requirements.txt` (flask, requests) y `Dockerfile`.
- [ ] `app.py` con una sola ruta `/` que devuelva texto.
- [ ] El servicio `front-flask` en el `docker-compose.yml`, puerto **8023**,
      con `API_FACTURAS_URL` y `depends_on: api-facturas`.

**Verificación:** `docker compose up -d --build` y `http://localhost:8023`
responde. *Todavía no habla con la API.*

## Fase 2 — `cliente_api.py`: el único que habla HTTP

- [ ] `_llamar()` con timeout, devolviendo `None` cuando no hay respuesta.
- [ ] `_cuerpo()` y `_mensajes()`, que conocen **los dos formatos** de error
      de FastAPI (diccionario y lista).
- [ ] `listar_productos()` — con el 204 devuelto como lista vacía.

**Verificación:** desde el contenedor,
`docker compose exec front-flask python -c "import cliente_api; print(cliente_api.listar_productos())"`
devuelve `(True, [...], [])`.

## Fase 3 — Ver: el listado

- [ ] `base.html` con la cabecera, el bloque de avisos y el pie.
- [ ] `estilos.css`.
- [ ] `productos/lista.html` con la tabla y el mensaje de tabla vacía.

**Verificación:** criterio 1. Y con la tabla vacía, la pantalla lo dice en
gris, no en rojo.

## Fase 4 — Crear

- [ ] `formulario.html` (sirve para crear y para editar).
- [ ] `crear_producto()` en `cliente_api`.
- [ ] La ruta `/productos/nuevo`, que **conserva lo digitado** ante un 422.

**Verificación:** criterios 2 y 3.

## Fase 5 — La pareja PUT/PATCH

- [ ] `obtener_producto()`, `reemplazar_producto()` y `actualizar_producto()`.
- [ ] Los **dos botones** con el mismo `name="verbo"`.
- [ ] En la ruta: PUT manda los tres campos; PATCH filtra los vacíos.
- [ ] El caso "no diligenció nada": avisa sin llamar a la API.

**Verificación:** criterios 4 y 5. *Es la fase que da sentido a la versión.*

## Fase 6 — Eliminar

- [ ] `eliminar_producto()`.
- [ ] La ruta por **POST** con `confirm()`.

**Verificación:** criterio 6.

## Fase 7 — La prueba de la separación

- [ ] Comprobar que `front_flask/` no importa ningún driver de base de datos.
- [ ] Comprobar que el servicio no recibe ninguna cadena de conexión.

**Verificación:** criterio 7 — apagar la API y ver la pantalla sin datos.

## Fase 8 — Cierre

- [ ] Los 7 criterios corridos por una persona.
- [ ] [9_checklist.md](9_checklist.md) firmada.
- [ ] El mapa de versiones y el README actualizados.
- [ ] Commit y **tag `v5`**.
