# Lista de chequeo — Versión 7

> **Versión 7** ([mapa](../0_mapa_versiones.md)) · Rige la
> [constitución](../../1_constitution.md). **La primera versión que TOCA LA
> API** desde que nació el front: hasta la v6 solo se le agregaban clientes;
> aquí la API estrena una entidad.
>
> | Documento | Contenido |
> |---|---|
> | [2_spec.md](2_spec.md) | QUÉ agrega la v7 y sus criterios |
> | [3_plan.md](3_plan.md) | CÓMO: dónde vive cada pieza de la autenticación |
> | [4_research.md](4_research.md) | Las decisiones, con lo que se descartó |
> | [5_data_model.md](5_data_model.md) | Las tablas que llevaban 6 versiones dormidas |
> | [6_contracts.md](6_contracts.md) | Los endpoints y las pantallas |
> | [7_quickstart.md](7_quickstart.md) | Arranque y smoke test |
> | [8_tasks.md](8_tasks.md) | El orden de construcción por fases |
> | [9_checklist.md](9_checklist.md) | La compuerta 3: se firma ANTES de programar |
> | [GUIA_IA7.md](GUIA_IA7.md) | Construirla con ayuda de una IA |

---

> **La compuerta 3.** Revisa **la ESPECIFICACIÓN, no el código**.

## Cómo se usa

- **Las casillas las marca una persona.** Una IA puede ayudar a evaluar, pero
  **no puede auto-aprobarse**.
- **Con una casilla en rojo no se escribe código.**

---

## A. Claridad

- [ ] Ningún requisito usa palabras sin definir.
- [ ] No queda ningún `[NECESITA ACLARACIÓN: …]`.

## B. Alcance

- [ ] El "NO incluye" es explícito, y dice que **los permisos son la v8**.
- [ ] Está justificado **por qué esta versión sí toca la API**, cuando
      ninguna anterior lo hizo.
- [ ] No se crea ninguna tabla: las cinco ya existían.

## C. Verificabilidad

- [ ] Cada criterio se puede **ejecutar**.
- [ ] El criterio 3 se comprueba **mirando la base**, no creyéndole a la API.
- [ ] El criterio 6 comprueba que los dos fallos dan **el mismo** mensaje.

## D. Coherencia con la constitución

- [ ] El chequeo de [3_plan §5](3_plan.md) está completo.
- [ ] La nota del Artículo 7 —qué deja de ser didáctico y qué no— está
      escrita.

## E. Trazabilidad

- [ ] Cada RF tiene al menos un criterio.
- [ ] Cada endpoint y cada pantalla salen de un RF.

## F. Las decisiones tienen razón, no gusto

- [ ] Está dicho **por qué bcrypt** y no un hash cualquiera.
- [ ] Está dicho **por qué sesión y no JWT**, y **cuándo cambiaría**.
- [ ] Está dicho por qué el front **aplana 401 y 404** aunque la API los
      distinga.

## G. Propia de esta versión: la honestidad sobre la seguridad

- [ ] **Está escrito, en los criterios, que el menú NO protege.**
- [ ] Existe un criterio que **comprueba el límite** (un no-admin llega por
      la URL), en vez de solo comprobar lo que sí funciona.
- [ ] La inconsistencia de las contraseñas dadas está **declarada como C1**,
      no tapada.
- [ ] Ningún documento sugiere que el sistema está protegido.

> Esta sección existe porque **un sistema que aparenta seguridad es peor que
> uno que no la tiene**: el segundo al menos no engaña a quien lo opera.

---

## Firma

```
Revisada por: ______________________     Fecha: ____________
```

**Sin esta firma no se escribe código.**
