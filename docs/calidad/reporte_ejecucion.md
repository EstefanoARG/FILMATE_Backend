# Reporte de ejecucion de pruebas

Fecha: 2026-07-08

## Resultado

Comando ejecutado:

```powershell
.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing --cov-report=xml -q
```

Resultado:

```text
32 passed
Coverage XML written to file coverage.xml
TOTAL: 62%
```

## Interpretacion

- La suite automatizada cubre flujos criticos de backend: salud API, OpenAPI, auth, usuarios, peliculas, RBAC, pagos, checkout y social.
- La cobertura global de 62% es una base defendible para la demo; los modulos de modelos/esquemas tienen alta cobertura, mientras reportes, reviews, tickets y configuracion requieren ampliacion futura.
- El mayor valor de la suite esta en pruebas basadas en riesgo:
  - acceso indebido a admin;
  - diferencia admin/superadmin;
  - pago rechazado sin efectos secundarios;
  - contratos sociales para evitar N+1.

## Evidencias generadas

- `coverage.xml`
- `tests/test_admin_security.py`
- `tests/test_payments_checkout.py`
- `tests/test_social_contracts.py`
- `docs/calidad/matriz_casos_prueba.md`

