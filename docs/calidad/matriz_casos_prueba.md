# Matriz de casos de prueba - FILMATE Backend

## Casos automatizados

| ID | Riesgo | Tecnica | Endpoint/Modulo | Entrada | Resultado esperado | Test |
| --- | --- | --- | --- | --- | --- | --- |
| TC-AUTH-01 | Acceso invalido | Caja negra | `/auth/login` | Password incorrecto | HTTP 401 | `test_login_wrong_password` |
| TC-AUTH-02 | Exposicion de password | Seguridad | `/auth/register` | Usuario valido | Respuesta sin `contrasena` | `test_register` |
| TC-RBAC-01 | Acceso admin sin token | OWASP A01/A07 | `/admin/movies/` | Sin `Authorization` | HTTP 401 | `test_admin_endpoint_requires_token` |
| TC-RBAC-02 | Cliente accede a admin | OWASP A01 | `/admin/movies/` | Token rol 2 | HTTP 403 | `test_client_role_cannot_access_admin_movies` |
| TC-RBAC-03 | Admin con permiso | Caja negra | `/admin/movies/` | Token rol 1 + permiso | HTTP 200 | `test_admin_with_required_permission_can_list_movies` |
| TC-RBAC-04 | Superadmin accede a roles | Caja negra | `/admin/roles/` | Token rol 3 | HTTP 200 | `test_superadmin_can_access_superadmin_routes` |
| TC-RBAC-05 | Admin comun accede a roles | OWASP A01 | `/admin/roles/` | Token rol 1 | HTTP 403 | `test_admin_cannot_access_superadmin_routes` |
| TC-PAY-01 | Metodos de pago ambiguos | Caja negra | `/client/payments/metodos-prueba` | GET | Lista tarjetas/Yape aprobados y rechazados | `test_payment_test_methods_document_success_and_rejection_paths` |
| TC-PAY-02 | OTP incorrecto | Caja negra | `/client/payments/tokenize/yape` | OTP `000000` | Token nulo + error | `test_yape_tokenization_rejects_wrong_otp` |
| TC-CHK-01 | Compra aprobada | Flujo E2E API | `/client/orders/checkout` | Token Yape aprobado + asiento | Transaccion, ticket y asiento ocupado | `test_checkout_approved_payment_creates_transaction_ticket_and_occupies_seat` |
| TC-CHK-02 | Pago rechazado ocupa asiento | Prueba basada en riesgo | `/client/orders/checkout` | Token Yape rechazado | HTTP 402, sin transaccion, asiento libre | `test_checkout_rejected_payment_is_atomic_and_does_not_occupy_seat` |
| TC-SOC-01 | N+1 en interacciones | Contrato/performance | `/interacciones/usuario/{id}` | Usuario con favorita | Interaccion incluye `pelicula` embebida | `test_user_interactions_embed_movie_to_avoid_frontend_n_plus_one` |
| TC-SOC-02 | N+1 en seguidores | Contrato/performance | `/client/seguidores/{id}/siguiendo` | Usuario siguiendo a otro | Respuesta incluye perfil `seguido` | `test_following_endpoint_embeds_followed_profile` |
| TC-SOC-03 | N+1 en colecciones | Contrato/performance | `/client/colecciones/usuario/{id}/detalles` | Coleccion con pelicula | Respuesta incluye `peliculas` | `test_collection_details_return_movies_in_single_response` |
| TC-MOV-01 | Busqueda por titulo | Caja negra | `/client/movies/search` | `q=Test` | Lista con coincidencias | `test_search_movies` |
| TC-API-01 | Contrato OpenAPI | Smoke | `/api/openapi.json` | GET | Schema contiene rutas criticas | `test_openapi` |

## Tecnicas usadas

- Caja negra: particiones validas/invalidas en login, pagos y busqueda.
- Caja blanca: verificacion de atomicidad antes/despues del cobro en checkout.
- Pruebas basadas en riesgo: RBAC, pago rechazado, asiento ocupado, rutas sociales lentas.
- Seguridad OWASP: Broken Access Control, Identification and Authentication Failures.

