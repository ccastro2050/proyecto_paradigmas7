# Quickstart — Versión 7: arranque y smoke test

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

## 1. Arranque

```powershell
docker compose up -d --build
```

| Qué | Dónde |
|---|---|
| **EL FRONT** (pide login) | http://localhost:8023 |
| La API — documentación | http://localhost:8021/docs |
| PostgreSQL · MariaDB · SQL Server | `15439` · `13338` · `11438` |

### Credenciales para probar (didácticas, de los datos dados)

| Correo | Contraseña | Roles | Cómo está guardada |
|---|---|---|---|
| `admin@correo.com` | `admin123` | Administrador | hash bcrypt |
| `cliente1@correo.com` | `cli123` | Cliente | **en claro** (C1) |
| `jefe@correo.com` | `jefe123` | Administrador, Cajero, Contador | **en claro** (C1) |

## 2. Smoke test — los 8 criterios

### 1 — La API estrena la entidad

```powershell
curl http://localhost:8021/api/usuario
#  → NO aparece la palabra "contrasena" por ninguna parte
curl http://localhost:8021/api/usuario/admin@correo.com
#  → {"email":"admin@correo.com","roles":["Administrador"]}
```

### 2 — Los cuatro desenlaces de verificar

```powershell
$H = @{"Content-Type"="application/json"}
# 200
curl -X POST http://localhost:8021/api/usuario/verificar-contrasena -H $H `
  -d '{"email":"admin@correo.com","contrasena":"admin123"}'
# 401 — clave equivocada
# 404 — usuario inexistente
# 422 — "noesuncorreo" no tiene forma de email
```

### 3 — Lo nuevo se guarda cifrado

Cree un usuario y **mire la base**:

```powershell
docker compose exec postgres psql -U paradigmas -d bdfacturas_postgres_local `
  -c "SELECT email, LEFT(contrasena,12) FROM usuario WHERE email='v7test@correo.com'"
#  → $2b$12$…   NO la contraseña
```

Y aun así se entra con ella.

### 4 — Sin sesión no hay sistema
Abra http://localhost:8023/producto **sin haber entrado**: debe mandarlo al
login. Igual `/facturas`.

### 5 — Entrar y salir
Entre como `admin@correo.com` / `admin123`. La barra debe mostrar el correo y
**Administrador**. Oprima **Salir** y compruebe que vuelve a pedir login.

### 6 — El front no delata usuarios
Pruebe **una clave equivocada** y luego **un correo que no existe**: los dos
deben decir exactamente *"Credenciales inválidas."*

### 7 — El menú cambia con el rol… y no protege

1. Como **admin**: el menú incluye **Usuarios** y **Vendedores**.
2. Salga y entre como `cliente1@correo.com` / `cli123`: **no** aparecen.
3. **Ahora escriba a mano** `http://localhost:8023/usuario`:

> **Se ve, con 200.** No es una falla del smoke test: es el límite conocido
> de la versión. El menú dibuja, la API todavía no pregunta quién llama, y
> eso es la v8. Ver [4_research §D3](4_research.md).

### 8 — Sin API no se puede ni entrar

```powershell
docker compose stop api-facturas
```

Intente entrar: *"El servicio no está disponible"*. Ni siquiera el login
funciona sin la API — porque **el front no comprueba contraseñas**.

```powershell
docker compose start api-facturas
```

## 3. Regresión: la v6 sigue viva

Con sesión iniciada, recorra las seis entidades y las facturas: todo lo de la
v6 funciona igual. Y los tres motores siguen respondiendo:

```powershell
$env:DB_PROVIDER="mariadb";   docker compose up -d api-facturas
$env:DB_PROVIDER="sqlserver"; docker compose up -d api-facturas
$env:DB_PROVIDER="postgres";  docker compose up -d api-facturas
```

## 4. Si algo falla

| Síntoma | Causa probable |
|---|---|
| `500` al abrir una entidad nueva del menú | Quedó una segunda lista de entidades sin actualizar (ver [3_plan §4](3_plan.md)) |
| El login siempre responde 404 | `verificar-contrasena` quedó declarado **después** de `/usuario/{email}` |
| `ModuleNotFoundError: bcrypt` | Falta reconstruir: `docker compose up -d --build` |
| `email-validator is not installed` | `EmailStr` necesita esa dependencia |
| Un usuario no puede entrar con la clave correcta | Puede ser de los que están en claro (C1) |
