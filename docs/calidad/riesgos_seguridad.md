# Riesgos, defectos y seguridad - FILMATE Backend

## Riesgos criticos identificados

| Riesgo | Impacto | Probabilidad | Mitigacion aplicada |
| --- | --- | --- | --- |
| Superadmin bloqueado por validacion incorrecta de rol | Alta | Media | Tests RBAC para rol 1 y rol 3. |
| Cliente accede a endpoints admin | Alta | Media | `get_current_admin` y `require_permiso`; pruebas 401/403. |
| Pago rechazado deja asiento ocupado | Alta | Alta | Checkout cobra antes de ocupar y test atomico lo valida. |
| Reuso de token de pago | Alta | Media | `payment_gateway_service.cobrar` consume token de un solo uso. |
| Social lento por N+1 desde frontend | Media | Alta | Endpoints devuelven pelicula/perfil/detalle embebido; tests de contrato. |
| Rutas dinamicas capturan rutas estaticas | Media | Media | Rutas especificas revisadas y cubiertas por smoke/OpenAPI. |

## Criterios OWASP aplicados

| OWASP Top 10 | Aplicacion en FILMATE |
| --- | --- |
| A01 Broken Access Control | RBAC por token, roles y permisos; pruebas admin/superadmin/cliente. |
| A02 Cryptographic Failures | Password hasheada con PBKDF2 + salt; no se expone en respuestas. |
| A03 Injection | Uso de SQLAlchemy ORM y parametros en queries. |
| A04 Insecure Design | Checkout atomico y token de pago de un solo uso. |
| A05 Security Misconfiguration | Tests usan `SKIP_DB_CONNECT=1` y no requieren secretos reales. |
| A07 Identification and Authentication Failures | Login invalido retorna 401; token requerido en admin. |
| A09 Security Logging and Monitoring Failures | Acciones admin relevantes generan logs de actividad. |

## Defectos relevantes ya cubiertos

- Error 401 para superadmin en frontend/admin: corregido y respaldado por pruebas backend RBAC.
- Checkout con endpoints fallback 404: consolidado en `/client/orders/checkout`.
- Social con demasiadas llamadas: endpoints devuelven datos embebidos.
- Configuracion publica faltante: endpoint `/client/configuracion/sistema`.

## Recomendaciones de mejora

- Agregar pruebas de carga con k6 para `/client/showtimes/range`, `/client/orders/checkout` y `/interacciones/usuario/{id}`.
- Agregar escaneo OWASP ZAP en entorno local o CI nocturno.
- Definir umbral de cobertura gradual: 65%, luego 75%, luego 80%.
- Separar tests unitarios y e2e con markers de pytest.

