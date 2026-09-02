# Guía de IA — Versión 7: construirla con ayuda de una IA

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

## 1. Antes de abrir el chat

Tenga a mano la constitución, los documentos de esta carpeta, **un
controlador y un repositorio existentes** (para que copie el patrón), el
`ensamblador.py` y el `front_flask/` de la v6.

**Lo más importante:** la IA no puede ver su base de datos. Si no le dice que
**la mitad de las contraseñas están en texto plano**, va a escribir una
verificación con bcrypt puro — y media tabla no podrá entrar, sin que se
entienda por qué.

## 2. El prompt

```text
Actúa como desarrollador del proyecto adjunto. Vamos a construir la VERSIÓN 7:
la autenticación. Es la PRIMERA versión que toca la API desde que nació el
front, y eso está justificado en 2_spec.md: desde la v5 estaba escrito que no
había login porque la API no exponía `usuario`.

CONTEXTO QUE NO PUEDES DEDUCIR Y NO DEBES INVENTAR:
- Las tablas usuario, rol, ruta, rol_usuario y rutarol EXISTEN desde la v1.
  NO se crea ninguna tabla, ni se altera. La base es infraestructura dada.
- La tabla usuario tiene DOS columnas: email (PK) y contrasena.
- LOS DATOS SEMBRADOS SON INCONSISTENTES: unos usuarios tienen hash bcrypt
  ($2a$..., $2b$...) y otros tienen la contraseña EN TEXTO PLANO
  ('jefe123', 'cli123'). La verificación debe aceptar LAS DOS FORMAS, o media
  tabla no puede entrar. Pero todo lo que la API ESCRIBA va cifrado. Esto está
  registrado como clarificación C1: no es un diseño, es una inconsistencia de
  los datos, y se declara en vez de taparse.
- La API es tri-motor: cada entidad tiene TRES repositorios (postgresql,
  mariadb, sqlserver) y se registra en las TRES familias del ensamblador.
  En SQL Server no hay LIMIT: es TOP (:limite).
- Los roles de un usuario salen de un JOIN: rol_usuario -> rol.

DÓNDE VA CADA COSA (esto es la lección de la versión):
- bcrypt va en el SERVICIO. No en el controller (que solo traduce HTTP) ni en
  el repositorio (habría que escribirlo tres veces, una por motor).
- El repositorio tiene DOS consultas distintas: obtener_por_email, que NO
  trae la contraseña, y obtener_hash, que trae SOLO eso. Así la única
  consulta que saca esa columna es la que la necesita.
- La API NUNCA devuelve la contraseña, ni el hash. El listado ni siquiera la
  selecciona.

EL ENDPOINT NUEVO: POST /api/usuario/verificar-contrasena con {email,
contrasena}. Cuatro desenlaces: 200 con {email, roles}, 401 si la contraseña
no coincide, 404 si el usuario no existe, 422 si el email no tiene forma de
email. DECLÁRALO ANTES de /api/usuario/{email}: FastAPI resuelve en orden y
al revés "verificar-contrasena" entraría como si fuera un email.

EN EL FRONT:
- /login y /logout. Toda otra ruta exige sesión, con UN DECORADOR, no con un
  if copiado en cada vista: a una vista se le puede olvidar el if y queda
  abierta sin que nadie lo note.
- La sesión guarda SOLO el correo y los roles. Nada de negocio, ninguna
  contraseña.
- El front APLANA 401 y 404 en un solo mensaje ("Credenciales inválidas").
  Que la API los distinga está bien; decírselo a quien toca la puerta es
  confirmarle qué correos existen.
- El menú se filtra por rol. PERO OJO: eso DIBUJA, no protege. Un no-admin
  que escriba /usuario la ve igual, y eso debe quedar escrito como límite
  conocido, no escondido. Los permisos de verdad son la v8.

NO INCLUYAS: JWT, permisos en la API, CRUD de rol o ruta, registro público,
recuperación de contraseña, expiración de sesión.

Empieza por la Fase 1 de 8_tasks.md. Al terminar cada fase PARA y dime cómo
verificarla.
```

> **Si es un agente con permiso de escribir:** `Escribe los archivos
> siguiendo EXACTAMENTE el patrón de la entidad empresa (mismo estilo de
> repositorio, servicio y controlador).`

## 3. Qué revisar de lo que entregue

| Revise | Por qué |
|---|---|
| ¿bcrypt aparece en el repositorio? | Está en la capa equivocada, y triplicado |
| ¿El listado trae `contrasena`? | Lo que se lee, algún día se filtra |
| ¿`verificar-contrasena` quedó después de `/{email}`? | FastAPI lo va a tomar como un email |
| ¿Guarda la contraseña en claro? | El requisito central de la versión |
| ¿Rechaza a los usuarios con contraseña en claro? | No leyó C1 |
| ¿El front dice "ese usuario no existe"? | Está delatando qué correos existen |
| ¿Copió un `if` de sesión en cada vista? | Debe ser un decorador |
| ¿Algún documento dice que el sistema está "protegido"? | El menú no protege: eso es la v8 |
| ¿Agregó la entidad al front en un solo sitio? | Si hay dos listas, se van a desincronizar |

## 4. Los tres destinos de un error

| Si… | La corrección va a |
|---|---|
| La IA no podía saberlo (las contraseñas mezcladas) | **La especificación** |
| La spec lo dice y la IA se equivoca **siempre** igual | **El prompt** |
| Falló una vez y al señalarlo lo arregló | **El estudiante** |

> **Dos ejemplos de esta versión, que pasaron de verdad:**
>
> 1. Al agregar `usuario` al front, la pantalla respondía **500**: había una
>    **segunda lista** de entidades escrita a mano. La corrección **no fue
>    agregar la que faltaba** —eso deja la trampa puesta— sino **quitar la
>    segunda lista**.
> 2. Se probó el menú por rol con `vendedor1@correo.com` suponiendo su
>    contraseña, y falló. No era un defecto del sistema: **era una suposición
>    sobre datos que no se habían mirado**. Se miró la tabla y se usó un
>    usuario cuya contraseña sí se conoce.
>
> Los dos son el mismo aprendizaje: **antes de cambiar código, averigüe si el
> problema es el código.**
