# Guía de IA — Versión 6: construirla con ayuda de una IA

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

## 1. Antes de abrir el chat

Tenga a mano `1_constitution.md`, los documentos de esta carpeta, el
`front_flask/` de la v5 y **los seis controladores de la API**.

**Lo más importante:** la IA no puede ver su sistema. Si no le dice que
`factura` no tiene PUT ni DELETE, va a asumir que las seis entidades son
iguales — **que es exactamente el error que esta versión enseña a no
cometer**.

## 2. El prompt

```text
Actúa como desarrollador del proyecto adjunto. Vamos a construir la VERSIÓN 6:
extender el front de la v5 (que ya cubre producto) a las seis entidades.

CONTEXTO QUE NO PUEDES DEDUCIR Y NO DEBES INVENTAR:
- La API ya está hecha y NO SE TOCA. Corre en api-facturas:8021. Desde el
  front se le llega por http://api-facturas:8021 (el NOMBRE del servicio,
  jamás localhost).
- La API NO es uniforme, y esto es lo más importante de la versión:
    * producto, persona, empresa, cliente y vendedor tienen CRUD COMPLETO
      (GET lista, GET uno, POST, PUT, PATCH, DELETE).
    * factura NO. Solo tiene: GET /api/factura, GET /api/factura/{numero},
      POST /api/factura y POST /api/factura/{numero}/anular.
      NO hay PUT, NI PATCH, NI DELETE de factura. Esa ausencia es una regla
      contable: una factura no se corrige ni se borra, se anula.
- Las llaves NO se llaman igual en todas: producto/persona/empresa usan
  {codigo}; cliente usa {id_cliente} y vendedor {id_vendedor} en la RUTA,
  pero la respuesta trae el campo como "id".
- cliente y vendedor tienen LLAVE GENERADA por la base: no se pide al crear.
- cliente y vendedor tienen LLAVES FORÁNEAS (fkcodpersona, fkcodempresa):
  van como <select> cargados desde la API, no como campos de texto.
- fkcodempresa es OPCIONAL: si va en blanco, NO SE ENVÍA en el cuerpo.
  Enviar "" es distinto de omitirlo, y la base los guarda distinto.
- Los errores de FastAPI llegan anidados bajo `detail`, con dos formas:
  diccionario para 400/404/500, y LISTA para los 422 de Pydantic.
- Al crear una factura, el número viene ANIDADO: la respuesta es
  {"factura": {"numero": 8, ...}, "productos": [...]}, NO {"numero": 8}.
- El listado responde 204 SIN CUERPO cuando no hay filas: no es un error.

QUÉ CONSTRUIR:
1. entidades.py: la DECLARACIÓN de las cinco entidades con CRUD (campos,
   etiquetas, cuáles son FK, si la llave se digita). factura NO va ahí.
2. Cuatro rutas GENÉRICAS que sirvan a las cinco, con DOS plantillas
   (templates/entidades/lista.html y formulario.html). NO escribas cinco
   copias de las pantallas.
3. Tres plantillas PROPIAS para factura (lista, detalle, nueva) y sus rutas.
   NO metas factura al patrón genérico con banderas tipo editable=False: si
   una entidad necesita banderas para caber, es que no cabe.
4. Un menú, que salga de la misma declaración y no de una lista aparte.

REGLAS QUE SE MANTIENEN DE LA v5:
- El front NO VALIDA NADA. Los inputs numéricos son type="text" a propósito:
  con type="number" el navegador rechazaría "abc" y el 422 no se vería.
- Ninguna vista usa `requests` directamente: todo pasa por cliente_api.
- El front NO suma el total de la factura: lo calcula un trigger en la base.
- TODO en español.

CRITERIO QUE DEBE PODER CUMPLIRSE: al apagar la API, LAS SEIS pantallas deben
seguir cargando y mostrar el aviso, sin datos.

Empieza por la Fase 1 de 8_tasks.md. Al terminar cada fase PARA y dime cómo
verificarla.
```

> **Si es un agente con permiso de escribir:** `Escribe los archivos en
> front_flask/. No toques nada dentro de api_facturas/.`

## 3. Qué revisar de lo que entregue

| Revise | Por qué |
|---|---|
| ¿Metió factura al patrón genérico? | El error central de la versión |
| ¿Inventó `PUT /api/factura`? | Le inventó endpoints a la API |
| ¿Copió las plantillas cinco veces? | Se saltó la decisión D1 |
| ¿El id de cliente aparece al crear? | Lo genera la base: pedirlo es mentir |
| ¿Las FK son campos de texto? | Deben ser `<select>` desde la API |
| ¿Envía `fkcodempresa=""`? | Vacío y ausente no son lo mismo |
| ¿Lee `respuesta["numero"]` al crear factura? | Viene anidado en `factura` |
| ¿Los numéricos son `type="number"`? | Tapó el 422 |
| ¿El menú es una lista escrita a mano? | Se va a desincronizar |

## 4. Los tres destinos de un error

| Si… | La corrección va a |
|---|---|
| La IA no podía saberlo (que factura no tiene DELETE) | **La especificación** |
| La spec lo dice y la IA se equivoca **siempre** igual | **El prompt** |
| Falló una vez y al señalarlo lo arregló | **El estudiante** |

> **Un ejemplo de esta versión, que pasó de verdad:** al construirla se supuso
> que el número de la factura venía en la raíz de la respuesta. La factura se
> creaba bien y el front se caía **después**, al redirigir. Eso no fue culpa
> de la IA ni del estudiante: **la spec no decía la forma de esa respuesta**.
> Por eso ahora la dice — y por eso está en el prompt de arriba.
