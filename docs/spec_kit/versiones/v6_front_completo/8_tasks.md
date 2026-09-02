# Tareas — Versión 6: el orden de construcción

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

## Fase 1 — La declaración

- [ ] `entidades.py` con `Campo`, `Entidad` y las **cinco** entidades.
- [ ] `factura` **NO** va aquí: no es un CRUD.

**Verificación:**
`docker compose exec front-flask python -c "from entidades import ENTIDADES; print(list(ENTIDADES))"`

## Fase 2 — `Recurso` en `cliente_api`

- [ ] La clase con las seis operaciones.
- [ ] `RECURSOS`, un objeto por entidad.
- [ ] Las funciones **sueltas** de factura: listar, obtener, crear, anular.

**Verificación:** `RECURSOS["persona"].listar()` devuelve `(True, [...], [])`.

## Fase 3 — El menú y las rutas genéricas

- [ ] `base.html` con el menú desde `context_processor`.
- [ ] `/<entidad>` y `entidades/lista.html`.
- [ ] Una entidad inexistente → **404**.

**Verificación:** criterio 1.

## Fase 4 — El formulario genérico

- [ ] `entidades/formulario.html`, que sirve para crear y editar.
- [ ] Los `<select>` de las llaves foráneas, cargados desde la API.
- [ ] La llave generada: **no se pide** al crear, **no se edita** al editar.
- [ ] El opcional vacío **se omite** del cuerpo.

**Verificación:** criterios 2, 4 y 5.

## Fase 5 — La pareja PUT/PATCH, en las cinco

- [ ] Los dos botones con `name="verbo"`.
- [ ] PUT manda todo; PATCH filtra lo vacío.
- [ ] PATCH sin nada: avisa **sin llamar a la API**.

**Verificación:** criterio 3, probado en **dos** entidades distintas.

## Fase 6 — Factura

- [ ] `facturas/lista.html` con el estado.
- [ ] `facturas/nueva.html`: maestro + cinco renglones como listas paralelas.
- [ ] `facturas/detalle.html` con el detalle y el total de la base.
- [ ] **OJO:** el número de la factura creada viene en `factura.numero`, no en
      la raíz. Y si viniera vacío, **no armar una URL con `None`**.

**Verificación:** criterio 6, incluido el 404 de `/facturas/<n>/editar`.

## Fase 7 — Anular

- [ ] La ruta por POST con confirmación.
- [ ] Ninguna ruta que edite ni borre una factura.

**Verificación:** criterio 7 — la factura sigue con su detalle.

## Fase 8 — Cierre

- [ ] Los 8 criterios corridos por una persona.
- [ ] [9_checklist.md](9_checklist.md) firmada.
- [ ] Mapa de versiones y README actualizados.
- [ ] Commit y **tag `v6`**.
