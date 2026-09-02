# Quickstart — Versión 5: arranque y smoke test

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

## 1. Arranque

```powershell
docker compose up -d --build
```

Un solo comando levanta **seis** servicios. La primera vez SQL Server tarda:
pide sus ~2 GB y hay que esperar a que responda.

| Qué | Dónde |
|---|---|
| **EL FRONT** | http://localhost:8023 |
| La API — documentación | http://localhost:8021/docs |
| PostgreSQL | `localhost:15439` |
| MariaDB | `localhost:13338` |
| SQL Server | `localhost:11438` |

## 2. Smoke test — los 7 criterios

Lo importante se hace **en el navegador**; abajo van los mismos pasos por
consola para dejar constancia.

### 1 y 2 — Arranca, y crear funciona

Abra http://localhost:8023 — debe redirigir al listado. Oprima
**Nuevo producto** y cree:

```
código P900 · nombre Teclado mecanico · stock 12 · valor 189000
```

Debe volver al listado con el aviso verde. Ahora compruebe que **la API lo
tiene**, que es la prueba de que el front no se lo guardó para él:

```powershell
curl http://localhost:8021/api/producto/P900
```

### 3 — El 422 se ve en pantalla

Cree otro producto con **`abc` en el stock**. Debe volver el formulario con:

```
stock: Input should be a valid integer, unable to parse string as an integer
```

Y el producto **no debe existir**:

```powershell
curl -i http://localhost:8021/api/producto/P901    # → 404
```

### 4 — La pareja PUT/PATCH, la lección de la versión

En **Editar** de P900, **borre el nombre** y:

1. Oprima **Reemplazar (PUT)** → aviso rojo:
   `nombre: String should have at least 1 character`
2. Sin tocar nada más, oprima **Actualizar lo diligenciado (PATCH)** →
   guarda y vuelve al listado.

**El mismo formulario, dos respuestas.**

### 5 — PATCH sin diligenciar nada

Borre los tres campos y oprima PATCH: avisa y no llama a la API.

### 6 — Eliminar

Oprima **Eliminar** y confirme. Debe salir del listado, y:

```powershell
curl -i http://localhost:8021/api/producto/P900    # → 404
```

### 7 — LA PRUEBA DE LA VERSIÓN

```powershell
docker compose stop api-facturas
```

Recargue http://localhost:8023/productos. Debe ver:

- La página **carga** — cabecera, estilos, pie.
- Un aviso rojo: *"El servicio no está disponible. ¿Está arriba la API?"*
- **Ni un solo producto.**

> Si el front pudiera llegar a la base por su cuenta, seguiría mostrando
> datos. **Que no los muestre es la demostración de que la separación es
> real**, y no solo una carpeta aparte.

```powershell
docker compose start api-facturas
```

## 3. Regresión: la API v1–v4 quedó intacta

```powershell
curl http://localhost:8021/api/producto
curl http://localhost:8021/api/persona
curl "http://localhost:8021/api/factura?limite=5"
```

Y el interruptor de motor de la v3 sigue funcionando:

```powershell
$env:DB_PROVIDER="mariadb"; docker compose up -d api-facturas
curl http://localhost:8021/api/producto
$env:DB_PROVIDER="postgres"; docker compose up -d api-facturas
```

## 4. Si algo falla

| Síntoma | Causa probable |
|---|---|
| El front dice *"servicio no disponible"* con todo arriba | `API_FACTURAS_URL` apunta a `localhost` en vez de `api-facturas` |
| `Connection refused` al abrir 8023 | El front no arrancó: `docker compose logs front-flask` |
| Los cambios en un `.html` no se ven | Recargue con Ctrl+F5: es caché del navegador |
| Un cambio en `app.py` no toma efecto | El código está montado y recarga solo; si no, `docker compose restart front-flask` |
