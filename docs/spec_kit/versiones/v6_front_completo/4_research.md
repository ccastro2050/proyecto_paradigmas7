# Investigación — Versión 6: decisiones y descartes

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

## D1 — Declarar las entidades, no copiar las pantallas

**Alternativas:** copiar las plantillas de la v5 cinco veces · un generador
de código que las escriba.

**Se eligió declarar.** Copiar deja diez plantillas que se van separando sola
—alguien arregla un error en cuatro y olvida la quinta—. Generar código deja
lo peor de las dos: archivos repetidos *y* una herramienta que mantener.

**Lo que cuesta:** una plantilla genérica es más difícil de leer que una
específica, porque habla de `d.campos` en vez de "nombre" y "stock". Se acepta
a cambio de que la verdad esté en un solo sitio, y por eso `entidades.py` está
comentado con cuidado.

**Cómo se sabe que la decisión aguanta:** agregar una entidad debe ser agregar
un objeto. Si algún día hay que tocar una plantilla para que quepa, la
decisión se quedó corta y hay que revisarla.

## D2 — Factura NO entra al patrón genérico

**Alternativa:** meterla con banderas —`editable=False`, `borrable=False`,
`accion_extra="anular"`— para que hubiera "un solo camino".

**Se descartó.** Esas banderas dirían que una factura es un CRUD con permisos
recortados. **No lo es.** Una factura es un documento contable: no se corrige
ni se borra, se anula, y su detalle viaja con ella. Las tres pantallas propias
dicen eso sin necesidad de explicarlo.

> **La señal que hay que aprender a leer:** cuando una entidad necesita tres
> banderas para caber en un patrón, **no cabe**. La API ya lo había dicho al
> no ofrecerle PUT ni DELETE — la ausencia de un endpoint es información.

## D3 — Las llaves foráneas se eligen, no se digitan

**Alternativa:** un campo de texto donde el usuario escriba el código, y que
la base rechace lo que no exista.

**Se descartó.** Funcionaría —la integridad referencial está en la base y no
depende del front—, pero obliga al usuario a saberse los códigos, y convierte
en error de pantalla algo que se puede evitar sin duplicar ninguna regla.

**Ojo con la diferencia:** esto **no es validar**. El front no comprueba que
la persona exista; solo ofrece las que la API le devolvió. Si entre que se
carga la lista y se envía el formulario alguien borra esa persona, **la API
responde con un error de integridad**, y así debe ser.

## D4 — El opcional en blanco se omite del cuerpo

**Alternativa:** enviarlo como cadena vacía.

**Se descartó** porque `""` y "no lo tiene" son cosas distintas, y la base las
guarda distinto: una cadena vacía y un `NULL`. Un cliente sin empresa debe
quedar con `fkcodempresa: null`, y es comprobable (criterio 4).

## D5 — Cinco renglones fijos en la factura

**Alternativa:** un botón "agregar renglón" con JavaScript.

**Se descartó por ahora**: exigiría el primer JavaScript del proyecto para un
problema que cinco filas resuelven. **Nadie ha pedido más de cinco.** Cuando
alguien lo pida, será una decisión con su razón — no una que se tomó "por si
acaso" (Artículo 1).

## D6 — El front no suma el total

El total lo calcula un trigger en la base y la API lo devuelve hecho. Si el
front lo recalculara habría **dos respuestas posibles a la misma pregunta**, y
el día que difieran nadie sabría cuál creer. La pantalla del detalle lo dice
en voz alta, porque es justo lo que un estudiante siente ganas de "arreglar".
