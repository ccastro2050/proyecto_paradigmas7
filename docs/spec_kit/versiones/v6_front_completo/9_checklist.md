# Lista de chequeo — Versión 6

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

> **La compuerta 3.** Revisa **la ESPECIFICACIÓN, no el código**: se corre
> cuando los documentos están escritos y **antes** de programar.

## Cómo se usa

- **Las casillas las marca una persona.** Una IA puede ayudar a evaluar, pero
  **no puede auto-aprobarse**.
- Se marca `[x]` solo cuando el criterio se cumple **hoy, en el documento**.
- **Con una casilla en rojo no se escribe código.**

---

## A. Claridad

- [ ] Ningún requisito usa palabras sin definir.
- [ ] No queda ningún `[NECESITA ACLARACIÓN: …]`.
- [ ] Cada RF explica UNA cosa.

## B. Alcance

- [ ] El "NO incluye" es explícito.
- [ ] Ningún requisito obliga a **tocar la API**.
- [ ] Lo que se deja para después está dicho por su nombre.

## C. Verificabilidad

- [ ] Cada criterio se puede **ejecutar**.
- [ ] El criterio 7 (anular no borra) comprueba que **el detalle sigue**.
- [ ] El criterio 8 se corre en **las seis** pantallas, no en una.

## D. Coherencia con la constitución

- [ ] El chequeo de [3_plan §5](3_plan.md) está completo.
- [ ] Ningún artículo tuvo que cambiarse.

## E. Trazabilidad

- [ ] Cada RF tiene al menos un criterio que lo cubre.
- [ ] Cada pantalla de [6_contracts](6_contracts.md) sale de un RF.
- [ ] Cada fase termina en una verificación.

## F. Las decisiones tienen razón, no gusto

- [ ] Cada decisión dice qué se descartó y por qué.
- [ ] La de **no meter factura en el patrón genérico** explica qué se pierde
      al forzarla.
- [ ] La de **elegir las FK en vez de digitarlas** aclara que **no es
      validar**.

## G. Propia de esta versión: ¿la generalización aguanta?

- [ ] Agregar una entidad es **agregar un objeto** a `entidades.py`, sin
      tocar plantillas.
- [ ] `entidades.py` **no contradice** a los modelos de la API.
- [ ] Está dicho, en algún documento, que si una entidad necesita banderas
      para caber en el patrón, **es que no cabe**.

---

## Firma

```
Revisada por: ______________________     Fecha: ____________
```

**Sin esta firma no se escribe código.**
