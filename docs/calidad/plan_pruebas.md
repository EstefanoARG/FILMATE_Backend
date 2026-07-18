# Plan integral de pruebas - FILMATE

## Alcance

Sistema bajo prueba: backend de FILMATE, API REST construida con FastAPI para autenticacion, cartelera, programacion de funciones, compra de entradas, pagos simulados, social, usuarios, roles, reportes y administracion.

Usuarios principales:
- Cliente: consulta cartelera, compra entradas, paga con Yape/tarjeta simulada, usa funciones sociales.
- Administrador: gestiona peliculas, cines, salas, funciones, ventas y configuracion.
- Superadmin: gestiona usuarios, roles, permisos y auditoria.

## Objetivo de calidad

Garantizar que los flujos criticos del negocio funcionen con seguridad, consistencia transaccional y tiempos razonables, alineando la estrategia con ISTQB, ISO/IEC 29119, IEEE 829 y criterios OWASP.

## Niveles de prueba

| Nivel | Objetivo | Evidencia actual |
| --- | --- | --- |
| Unitario | Validar funciones puras y reglas aisladas. | `tests/test_auth.py`, `tests/test_payments_checkout.py` |
| Integracion | Validar repositorios, servicios y API con BD SQLite en memoria. | `tests/conftest.py`, `tests/test_movies.py`, `tests/test_social_contracts.py` |
| Sistema/API | Validar endpoints reales con `TestClient`. | `tests/test_app.py`, `tests/test_admin_security.py` |
| Aceptacion tecnica | Validar flujos de negocio end-to-end del backend. | checkout aprobado/rechazado, RBAC admin/superadmin |
| Regresion | Evitar que cambios en social, pagos o roles rompan flujos ya corregidos. | Suite completa `pytest` |

## Tipos de prueba priorizados

| Tipo | Justificacion |
| --- | --- |
| Funcional API | El backend expone la mayoria de funcionalidades por endpoints. |
| Seguridad/RBAC | Existen roles diferenciados: cliente, administrador y superadmin. |
| Transaccional | La compra no debe ocupar asientos si el pago falla. |
| Regresion | Se han corregido fallos de 401, checkout y social lento. |
| Performance contractual | Social debe devolver datos embebidos para evitar N+1 desde frontend. |
| Smoke/OpenAPI | La API debe iniciar y publicar documentacion valida. |

## Ambiente de prueba

- Python desde `venv`.
- Base de datos SQLite en memoria para pruebas automatizadas.
- `SKIP_DB_CONNECT=1` en tests para no depender de MySQL.
- FastAPI `TestClient`.
- Cobertura con `pytest-cov`.

## Comandos

```powershell
cd FILMATE_Backend
.\venv\Scripts\python.exe -m pytest -q
.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing --cov-report=xml -q
```

## Criterios de entrada

- Backend instala dependencias de `requirements.txt`.
- Tests pueden crear esquema con SQLAlchemy.
- No se requiere seed SQL completo para la suite automatizada.

## Criterios de salida

- 100% de tests automatizados pasan.
- Flujos criticos cubiertos: login, RBAC, movies, checkout, pagos, social.
- Cobertura reportada e interpretada.
- Riesgos criticos documentados.

