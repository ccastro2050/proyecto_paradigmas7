# Contratos — Versión 7: endpoints y pantallas

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

## PARTE A — La API: `http://localhost:8021`

### A.0 Los endpoints nuevos

| Ruta | Método | Qué hace |
|---|---|---|
| `/api/usuario` | GET | Lista **sin contraseñas** (204 si vacío) |
| `/api/usuario/{email}` | GET | El usuario **con sus roles** |
| `/api/usuario` | POST | Crea, **cifrando** la contraseña |
| `/api/usuario/{email}` | PUT | Reemplazo completo |
| `/api/usuario/{email}` | PATCH | Parcial |
| `/api/usuario/{email}` | DELETE | Elimina |
| **`/api/usuario/verificar-contrasena`** | **POST** | **El login** |

> **Orden importa:** `verificar-contrasena` se declara **antes** que
> `/usuario/{email}`. FastAPI resuelve en orden, y al revés
> "verificar-contrasena" entraría como si fuera un email.

### A.1 Listar — la contraseña no está

```
GET /api/usuario?limite=3
→ 200 {"tabla":"usuario","limite":3,"total":3,
       "datos":[{"email":"admin@correo.com"}, …]}
```

**No hay campo `contrasena`.** No es que se filtre al serializar: **el SELECT
no la pide**. Lo que no se lee, no se filtra.

### A.2 Uno, con sus roles

```
GET /api/usuario/admin@correo.com
→ 200 {"email":"admin@correo.com","roles":["Administrador"]}
```

El JOIN lo hace quien tiene los datos.

### A.3 Crear — se guarda cifrada

```
POST /api/usuario   {"email":"nuevo@x.com","contrasena":"clave123"}
→ 200 {"estado":200,"mensaje":"Usuario creado exitosamente."}
```

En la base queda `$2b$12$…`, comprobable (criterio 3).

- Email repetido → **500**: la llave la defiende la base.
- Email sin forma de email → **422**, de Pydantic.

### A.4 **Verificar credenciales** — los cuatro desenlaces

```
POST /api/usuario/verificar-contrasena
body {"email":"admin@correo.com","contrasena":"admin123"}
→ 200 {"email":"admin@correo.com","roles":["Administrador"]}

body {… "contrasena":"nooo"}
→ 401 {"detail":{"estado":401,"mensaje":"Credenciales inválidas.",
                 "detalle":"El usuario o la contraseña no coinciden."}}

body {"email":"nadie@correo.com", …}
→ 404

body {"email":"noesuncorreo", …}
→ 422
```

**El 401 no dice "la contraseña está mal"**: eso confirmaría que el usuario
existe. La API distingue por dentro; lo que responde afuera no lo delata.

## PARTE B — El front: `http://localhost:8023`

### B.0 El mapa

| Ruta | ¿Exige sesión? | Qué hace |
|---|---|---|
| `/login` | **No** | El formulario y la validación |
| `/logout` | **No** | Cierra la sesión |
| Todas las demás | **Sí** | Sin sesión, redirigen (302) al login |

### B.1 `/login`

| Caso | Resultado |
|---|---|
| Correcto | **302** al inicio + *"Bienvenido, correo (roles)"* |
| Clave equivocada | **200** con *"Credenciales inválidas"* y el correo puesto |
| Usuario inexistente | **200** con **el MISMO mensaje** |
| API caída | **200** con *"El servicio no está disponible"* |

**La contraseña nunca vuelve al formulario**; el correo sí.

### B.2 La barra, con sesión

```
Facturas   Productos Personas Empresas Clientes Vendedores Usuarios Facturas
                                     admin@correo.com  Administrador  [Salir]
```

Sin sesión **no hay menú**: desde afuera solo existe `/login`.

### B.3 El menú por rol

| Rol | Ve en el menú |
|---|---|
| **Administrador** | Productos · Personas · Empresas · Clientes · **Vendedores** · **Usuarios** · Facturas |
| Cliente, Vendedor… | Productos · Personas · Empresas · Clientes · Facturas |

> **Y esto es lo que hay que entender de la v7:** un Cliente que escriba
> `/usuario` en el navegador **la ve igual, con 200**. El menú **dibuja**, no
> protege. Está así en el criterio 7 a propósito — para que nadie confunda
> una comodidad de interfaz con una barrera.

## PARTE C — Los avisos

| Origen | Se ve como |
|---|---|
| Credenciales malas o usuario inexistente | *"Credenciales inválidas."* |
| Ruta sin sesión | *"Entre al sistema para continuar."* |
| API caída | *"El servicio no está disponible. ¿Está arriba la API?"* |
| 422 de Pydantic | una línea por campo |
