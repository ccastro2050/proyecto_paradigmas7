# Guía de IA — Versión 5: construir el front con ayuda de una IA

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

## 1. Antes de abrir el chat

La IA no adivina el contexto: hay que dárselo. Tenga a mano

- `docs/spec_kit/1_constitution.md`
- Los documentos de **esta** carpeta (2 a 8).
- El `docker-compose.yml` y `api_facturas/controllers/producto_controller.py`.

**Lo más importante:** la IA **no puede ver su sistema**. Si no le dice que la
API responde en `api-facturas:8021` y que sus errores llegan anidados bajo
`detail`, se lo va a inventar — y va a fallar en la primera pantalla.

## 2. El prompt

Péguelo con los documentos adjuntos. Sirve igual en un chat o en un agente;
si es un agente que puede escribir archivos, agregue la línea final.

```text
Actúa como desarrollador del proyecto adjunto. Vamos a construir la VERSIÓN 5:
el front en Flask que consume la API que ya existe.

CONTEXTO QUE NO PUEDES DEDUCIR Y NO DEBES INVENTAR:
- La API ya está hecha y NO SE TOCA. Corre en el contenedor `api-facturas`,
  puerto 8021. Desde el front se le llega por http://api-facturas:8021
  (el NOMBRE del servicio, jamás localhost: dentro del contenedor del front,
  localhost es el front mismo).
- La API expone SEIS controladores: cliente, empresa, factura, persona,
  producto, vendedor. NO hay controlador de usuario, así que NO HAY LOGIN
  en esta versión. Si crees que hace falta, dilo — pero no lo agregues.
- La API es FastAPI y sus errores llegan SIEMPRE anidados bajo la llave
  `detail`, con DOS formas distintas:
    * 400/404/500: {"detail": {"estado":…, "mensaje":…, "detalle":…}}
    * 422 (Pydantic): {"detail": [{"loc": ["body","stock"], "msg": …}]}
  El front debe entender las dos.
- El listado responde 204 SIN CUERPO cuando no hay filas. Eso NO es un error.
- El front va en el puerto 8023 y se agrega al docker-compose.yml existente
  como un servicio nuevo, con su propio Dockerfile. NO recibe ninguna cadena
  de conexión: no debe poder llegar a la base de datos ni por accidente.

QUÉ CONSTRUIR: solo la entidad producto — listar, crear, editar y eliminar.
Las otras cinco entidades NO se tocan (regla: una versión no anticipa a la
siguiente).

REGLAS DE ARQUITECTURA:
- Dos archivos de Python: app.py (las vistas) y cliente_api.py (el ÚNICO que
  habla HTTP). Ninguna vista debe usar `requests` directamente.
- cliente_api devuelve tuplas (ok, datos, errores). Las vistas no saben qué
  es un 422.
- El front NO VALIDA NADA. Esa regla ya vive en los modelos Pydantic de la
  API; repetirla aquí le daría dos dueños. Los inputs numéricos van como
  type="text" a propósito: con type="number" el navegador rechazaría "abc"
  antes de enviarlo y el 422 no se vería nunca.
- La pantalla de edición tiene UN formulario con DOS botones submit
  (name="verbo", value="put" y value="patch"). PUT manda los tres campos
  aunque estén vacíos —por eso un campo en blanco es 422—; PATCH manda solo
  los diligenciados. Esa pareja es la lección de la versión.
- Eliminar va por POST con confirmación, nunca por un enlace GET.
- Jinja2 y CSS a mano. Sin Bootstrap, sin React, sin JavaScript de framework.
- TODO en español: rutas, plantillas, avisos, comentarios y nombres.

CRITERIO QUE DEBE PODER CUMPLIRSE (el que define la versión): al apagar la
API con `docker compose stop api-facturas`, la pantalla /productos debe
seguir CARGANDO —con su cabecera y sus estilos— y mostrar el aviso "el
servicio no está disponible", SIN datos. Si tu diseño no puede cumplir esto,
está mal.

Empieza por la Fase 1 de 8_tasks.md. Al terminar cada fase, PARA y dime cómo
verificarla. No pases a la siguiente sin que yo confirme.
```

> **Última línea, solo si es un agente con permiso de escribir:**
> `Escribe los archivos directamente en front_flask/ y modifica el
> docker-compose.yml. No toques nada dentro de api_facturas/.`

## 3. Qué revisar de lo que entregue

| Revise | Por qué |
|---|---|
| ¿Alguna vista usa `requests`? | Se saltó la capa: eso va en `cliente_api` |
| ¿Los inputs son `type="number"`? | Tapó el 422. Deben ser `type="text"` |
| ¿Convierte `stock` a `int` antes de enviar? | Se adelantó a la validación de la API |
| ¿Agregó login? | Le inventó un endpoint a la API |
| ¿Lee el error como `r.json()["mensaje"]`? | Olvidó que FastAPI anida bajo `detail` |
| ¿El 204 lo trata como error? | La tabla vacía no es una falla |
| ¿Le puso una cadena de conexión al front? | Rompió la versión entera |

## 4. Los tres destinos de un error

Cuando algo salga mal, la corrección va a **uno** de tres lugares, y elegir
bien es lo que hace que la próxima vez salga mejor:

| Si… | La corrección va a |
|---|---|
| La IA no podía saberlo (el puerto, la forma del error) | **La especificación** |
| La spec lo dice, pero la IA se equivoca **siempre** en lo mismo | **El prompt** |
| Falló una vez y al señalarlo lo arregló | **El estudiante**: se corrige y sigue |

Confundirlos sale caro: engordar el prompt con cosas que fallaron una sola vez
lo vuelve ilegible, y parchar a mano lo que la spec no dice condena a repetir
el error en la versión siguiente.
