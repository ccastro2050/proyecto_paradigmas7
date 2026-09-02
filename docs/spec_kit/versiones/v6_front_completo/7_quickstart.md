# Quickstart — Versión 6: arranque y smoke test

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

## 1. Arranque

```powershell
docker compose up -d --build
```

| Qué | Dónde |
|---|---|
| **EL FRONT** | http://localhost:8023 |
| La API — documentación | http://localhost:8021/docs |
| PostgreSQL · MariaDB · SQL Server | `15439` · `13338` · `11438` |

## 2. Smoke test — los 8 criterios

### 1 — Las seis pantallas
Abra http://localhost:8023 y recorra el menú: Productos, Personas, Empresas,
Clientes, Vendedores y Facturas. Luego pruebe una que no existe:

```powershell
curl -i http://localhost:8023/noexiste      # → 404
```

### 2 y 3 — El CRUD genérico y la pareja PUT/PATCH
En **Personas**, cree `Z900 · Ana Prueba · ana@x.com · 3001234567`. Compruebe
que **la API la tiene**:

```powershell
curl http://localhost:8021/api/persona/Z900
```

Ahora **Editar**, borre el nombre y oprima los dos botones:

1. **Reemplazar (PUT)** → `nombre: String should have at least 1 character`
2. **Actualizar (PATCH)** → guarda y vuelve al listado

### 4 — La llave foránea es una lista
En **Clientes → Crear**: `Persona` es un `<select>` con las personas que
existen, y **no hay campo para el id**: lo genera la base.

Elija `Z900`, ponga crédito `750000`, **deje la empresa en blanco** y cree.
Compruebe que quedó en `null` y no en cadena vacía:

```powershell
curl http://localhost:8021/api/cliente
#  → "fkcodempresa": null
```

### 5 — El 422 en una entidad con FK
Cree otro cliente con **`mucho`** en el crédito:

```
credito: Input should be a valid decimal
```

### 6 — Factura: se crea, pero no se edita
En **Facturas → Nueva**, elija cliente y vendedor, y dos renglones. Al crear,
va al detalle: el total lo calculó la base.

Ahora compruebe que **la ruta de edición no existe**:

```powershell
curl -i http://localhost:8023/facturas/1/editar     # → 404
```

Y que sin renglones el front avisa **sin llamar a la API**.

### 7 — Anular no es borrar
En el detalle, **Anular**. La factura sigue en la lista, atenuada, con estado
`anulada`:

```powershell
curl http://localhost:8021/api/factura/1
#  → "estado": "anulada", y "productos" INTACTO
```

### 8 — Sin API, ninguna pantalla tiene datos

```powershell
docker compose stop api-facturas
```

Recorra **las seis**: todas cargan, todas muestran *"El servicio no está
disponible"*, **ninguna muestra datos**.

```powershell
docker compose start api-facturas
```

## 3. Regresión

La API v1–v4 no se tocó, y sigue sirviendo a los tres motores:

```powershell
curl http://localhost:8021/api/producto
$env:DB_PROVIDER="mariadb";   docker compose up -d api-facturas
$env:DB_PROVIDER="sqlserver"; docker compose up -d api-facturas
$env:DB_PROVIDER="postgres";  docker compose up -d api-facturas
```

## 4. Si algo falla

| Síntoma | Causa probable |
|---|---|
| Un `<select>` de FK sale vacío | No hay registros en esa entidad: créelos primero |
| El cliente queda con `fkcodempresa: ""` | Se está enviando el opcional vacío en vez de omitirlo |
| Al crear una factura sale error tras crearla | El número viene **anidado** en `factura.numero`, no en la raíz |
| Una entidad nueva no sale en el menú | El menú sale de `entidades.py`: agréguela ahí |
