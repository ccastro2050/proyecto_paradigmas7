# Contratos HTTP — Versión 3: CERO endpoints nuevos (esa es la gracia)

> El contrato de la API es EXACTAMENTE el de las versiones anteriores:
> los 35 endpoints de la [v1](../v1_producto_postgres/6_contracts.md) y la
> [v2](../v2_mas_tablas/6_contracts.md) siguen vigentes **tal cual, con
> ambos motores**. Esta página existe para decir formalmente qué NO
> cambió — y la única línea que sí.

---

## 1. Lo único que cambia: el diagnóstico

```
GET /
→ 200 { "mensaje": "API Facturas funcionando", "version": "v3",
        "motor": "postgres", "documentacion": "/docs" }
```

`motor` refleja `DB_PROVIDER` (`postgres` por defecto; `mariadb` con el
interruptor). Es el único campo nuevo de toda la versión.

## 2. Lo que formalmente NO cambia (y el criterio 3 verifica)

| Grupo | Endpoints | Con `postgres` | Con `mariadb` |
|---|---|---|---|
| producto (v1) | 7 | idénticos | idénticos |
| persona, empresa, cliente, vendedor (v2) | 24 | idénticos | idénticos |
| factura (v2) | 4 | idénticos (CALL con INOUT) | idénticos (CALL + `SELECT @salida`) |

Los códigos son los mismos: 200 · 204 lista vacía · 400 negocio · 404 no
existe · 409 ya anulada · 422 Pydantic · 500 el motor.

**Matiz honesto del contrato:** el campo `detalle` de los errores 500
transporta el mensaje del MOTOR, y cada motor redacta distinto
(PostgreSQL: "viola la llave foránea…" · MariaDB: "Cannot add or update a
child row: a foreign key constraint fails…"). El contrato fija `estado` y
`mensaje`; `detalle` es informativo y depende del dialecto — igual que
desde la v1. Un detalle más fino: los números `NUMERIC/DECIMAL` pueden
serializar con distinta cantidad de decimales (5000000.0 vs 5000000.00) —
el VALOR es el mismo; los formatos exactos por campo no son contrato.
