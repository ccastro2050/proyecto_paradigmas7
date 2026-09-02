# Investigación — Versión 7: decisiones y descartes

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

## D1 — bcrypt, y no un hash cualquiera

**Alternativas:** guardar en claro (como venían la mitad de los datos) ·
MD5 o SHA-256 a secas · bcrypt.

**Se eligió bcrypt** porque está hecho para contraseñas: es **lento a
propósito** y lleva **sal incorporada**, así que dos personas con la misma
contraseña tienen hashes distintos. SHA-256 es rápido, y ser rápido es
justamente el defecto cuando alguien se roba la tabla y prueba millones de
combinaciones por segundo.

**Lo que cuesta:** una dependencia más, y que verificar tarde unos
milisegundos. Los dos precios están bien pagados.

## D2 — La sesión de Flask, no JWT

**Alternativas:** un token JWT que el front guarde y mande en cada llamada.

**Se descartó por ahora.** JWT resuelve un problema que este sistema **no
tiene**: varios clientes distintos, o una API sin estado detrás de un
balanceador. Aquí hay **un** front hablando con **una** API, y una cookie
firmada hace el trabajo con dos líneas.

**Cuándo cambiaría:** el día que haya un segundo cliente —una aplicación
móvil, otro servicio— la cookie deja de servir y JWT se gana su sitio. **Ese
día será una versión, con su spec**; no algo que se metió antes por si acaso
(Artículo 1).

## D3 — El menú DIBUJA, no protege — y se dice

**Alternativa:** dejar que el filtro del menú pareciera seguridad y no
mencionarlo.

**Se descartó, y es la decisión más importante de la versión.** Esconder una
opción del menú **no impide nada**: quien escriba `/usuario` en la barra del
navegador la ve igual. La seguridad de verdad tendría que estar **en la API**
—que hoy no pregunta quién llama— y esa es la v8.

Por eso el **criterio 7 comprueba las dos cosas**: que el Cliente no vea
*Usuarios* en el menú, **y que la vea si escribe la URL**. Un criterio que
solo probara lo primero dejaría creer que hay una protección que no existe.

> **Un sistema que aparenta seguridad es peor que uno que no la tiene**,
> porque el segundo al menos no engaña a quien lo opera.

## D4 — Se aceptan las contraseñas en claro que ya estaban

**Alternativa:** exigir bcrypt siempre, y que `jefe@correo.com` y
`cliente1@correo.com` no puedan entrar hasta que alguien los migre.

**Se descartó** porque dejaría el sistema dado a medio funcionar sin avisar
por qué. Se aceptan las dos formas **y se declara** (C1): los usuarios en
claro son **deuda visible**, no un diseño. Todo lo que la API escriba de
ahora en adelante va cifrado, así que la deuda se paga sola a medida que
cambien sus contraseñas.

**Lo que se pierde:** durante un tiempo conviven dos formatos. Se acepta a
cambio de no romper los datos dados ni inventar una migración que nadie pidió
(Artículo 5).

## D5 — El front aplana 401 y 404 en un solo mensaje

**Alternativa:** mostrar "ese usuario no existe" cuando la API responde 404.

**Se descartó.** Un formulario que distingue los dos casos es un formulario
que **confirma qué correos están registrados**: se prueban correos hasta que
uno responda distinto.

**Que la API sí los distinga no es contradictorio**: la API le habla a un
programa que puede necesitar el detalle; la pantalla le habla a alguien que
está tocando la puerta. **La misma información no se cuenta igual a los dos.**

## D6 — Un decorador para exigir sesión

**Alternativa:** un `if "email" not in session` al principio de cada vista.

**Se descartó** porque el olvido no avisa: la vista a la que se le escape el
`if` **funciona perfectamente** — solo que abierta. El decorador se ve en la
línea de arriba de cada ruta, y una revisión de código lo encuentra a simple
vista.
