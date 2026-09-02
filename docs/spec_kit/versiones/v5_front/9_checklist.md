# Lista de chequeo — Versión 5

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

> **La compuerta 3.** Revisa **la ESPECIFICACIÓN, no el código**: se corre
> cuando los documentos están escritos y **antes** de programar.

## Cómo se usa

- **Las casillas las marca una persona.** Una IA puede ayudar a evaluar y
  señalar dudas, pero **no puede auto-aprobarse**: quien firma responde.
- Se marca `[x]` solo cuando el criterio se cumple **hoy, en el documento**.
- **Con una casilla en rojo no se escribe código.**

---

## A. Claridad

- [ ] Ningún requisito usa palabras sin definir (*amigable, rápido, bonito*).
- [ ] No queda ningún `[NECESITA ACLARACIÓN: …]` sin resolver.
- [ ] Cada RF explica UNA cosa.

## B. Alcance

- [ ] El "NO incluye" de [2_spec §2](2_spec.md) es explícito.
- [ ] Ningún requisito obliga a **tocar la API**: si alguno lo hiciera, no es
      de esta versión (regla 3 del mapa).
- [ ] Las otras cinco entidades quedan fuera, dichas por su nombre.

## C. Verificabilidad

- [ ] Cada criterio de aceptación se puede **ejecutar**, y dice con qué se
      comprueba.
- [ ] El criterio 7 —apagar la API— está escrito como un paso reproducible.
- [ ] Los tres formatos de error tienen su comportamiento definido.

## D. Coherencia con la constitución

- [ ] El chequeo de [3_plan §4](3_plan.md) está completo, artículo por
      artículo.
- [ ] Ningún artículo tuvo que cambiarse para que esta versión quepa.

## E. Trazabilidad

- [ ] Cada RF tiene al menos un criterio que lo cubre.
- [ ] Cada pantalla de [6_contracts](6_contracts.md) sale de un RF.
- [ ] Cada fase de [8_tasks](8_tasks.md) termina en una verificación.

## F. Las decisiones tienen razón, no gusto

- [ ] Cada decisión de [4_research](4_research.md) dice qué se descartó y
      por qué.
- [ ] La decisión de **no poner login** cita el hecho que la obliga: la API
      no expone `usuario`.
- [ ] La decisión de **no validar en el front** dice qué se pierde.

---

## Firma

Cuando todas las casillas estén en verde:

```
Revisada por: ______________________     Fecha: ____________
```

**Sin esta firma no se escribe código.**
