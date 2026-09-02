# Tareas — Versión 7: el orden de construcción

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

## Fase 1 — El modelo y las interfaces

- [ ] `models/usuario.py`: Usuario, UsuarioReemplazo, UsuarioActualizar y
      **Credenciales**.
- [ ] `i_repositorio_usuario.py`, con `obtener_hash` **separado** de
      `obtener_por_email`.
- [ ] `i_servicio_usuario.py`, con `verificar`.

**Verificación:** los módulos importan sin error.

## Fase 2 — Los tres repositorios

- [ ] PostgreSQL, MariaDB y SQL Server (este con `TOP (:limite)`).
- [ ] El listado **no selecciona** la contraseña.
- [ ] `obtener_roles` con el JOIN a `rol_usuario` y `rol`.

**Verificación:** desde el contenedor, `obtener_roles("admin@correo.com")`
devuelve `["Administrador"]`.

## Fase 3 — El servicio: bcrypt vive aquí

- [ ] `_cifrar` y `_coincide`, que acepta **hash y texto plano** (C1).
- [ ] `verificar`: `LookupError` si no existe, `PermissionError` si no
      coincide.
- [ ] El CRUD, cifrando siempre al escribir.

**Verificación:** la prueba sin base de datos, con un repositorio de
mentiras, pasa.

## Fase 4 — El controlador

- [ ] Los siete endpoints.
- [ ] **`verificar-contrasena` declarado ANTES de `/usuario/{email}`.**
- [ ] `PermissionError` → **401**, con un detalle que no delata.

**Verificación:** criterios 1, 2 y 3.

## Fase 5 — El cableado

- [ ] `usuario` en las **tres** familias del ensamblador.
- [ ] `crear_servicio_usuario()`.
- [ ] El router en `main.py`.
- [ ] `bcrypt` y `email-validator` en `requirements.txt`.

**Verificación:** `/api/usuario` responde con los tres valores de
`DB_PROVIDER`.

## Fase 6 — El front entra al sistema

- [ ] `verificar_credenciales()` en `cliente_api`.
- [ ] `login.html`.
- [ ] `/login` y `/logout`, con la sesión guardando **correo y roles**.
- [ ] **401 y 404 aplanados** a un solo mensaje.

**Verificación:** criterios 5 y 6.

## Fase 7 — La puerta y el menú

- [ ] El decorador `exige_sesion` en **todas** las rutas menos login/logout.
- [ ] `USUARIO` en `entidades.py`, con `roles=("Administrador",)`.
- [ ] `visibles_para()` y el menú filtrado.
- [ ] **Comprobar que no quedó una segunda lista de entidades** en
      `cliente_api` (ver [3_plan §4](3_plan.md)).

**Verificación:** criterios 4 y 7 — **incluida la parte que comprueba que
el menú NO protege**.

## Fase 8 — Cierre

- [ ] Los 8 criterios corridos por una persona.
- [ ] La regresión de la v6, con sesión.
- [ ] [9_checklist.md](9_checklist.md) firmada.
- [ ] Mapa y README actualizados.
- [ ] Commit y **tag `v7`**.
