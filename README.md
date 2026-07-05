# Filmate — Backend API

API REST para la plataforma de cine **Filmate**, construida con **FastAPI** + **SQLAlchemy** + **MySQL**.

---

## Estructura del Proyecto

```
backend/
├── app/
│   ├── core/              # Configuración, DB, dependencias, app factory
│   ├── models/            # Modelos ORM (SQLAlchemy)
│   ├── repositories/      # Capa de acceso a datos
│   ├── routes/            # Endpoints de la API
│   │   ├── admin_*.py     # Rutas de administración (/admin/...)
│   │   ├── client_*.py    # Rutas de cliente (/client/...)
│   │   └── *.py           # Rutas públicas
│   ├── schemas/           # Validación Pydantic
│   ├── services/          # Lógica de negocio
│   ├── utils/             # PDF, QR, etc.
│   ├── websocket/         # Tiempo real (asientos)
│   ├── main.py            # Punto de entrada (app = create_app())
│   └── core/app.py        # Factory create_app()
├── tests/
│   ├── conftest.py        # Configuración de pruebas (SQLite, fixtures)
│   ├── test_app.py        # Pruebas de salud de la app
│   ├── test_auth.py       # Pruebas de autenticación
│   ├── test_movies.py     # Pruebas de películas
│   └── test_users.py      # Pruebas de usuarios
├── scripts/
│   └── DSOOMDAG4v2.3.sql  # Esquema de base de datos
├── pyproject.toml          # Configuración de proyecto y herramientas
├── requirements.txt
└── .env
```

---

## Requisitos

- Python 3.11+
- MySQL 8.0+

---

## Instalación

```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

Crear `.env` en `backend/`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=admin
DB_NAME=filmate_db

TMDB_API_KEY=tu_api_key_aqui
TMDB_LANG=es-ES
```

Ejecutar el script SQL en MySQL:

```bash
mysql -u root -p < scripts/DSOOMDAG4v2.3.sql
```

> La pasarela de pagos (`app/services/payment_gateway_service.py`) está **simulada localmente** — no requiere ninguna variable de entorno ni cuenta externa (ver sección [Pasarela de pagos](#pasarela-de-pagos-simulada)).

---

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Servidor en `http://localhost:8000` — Swagger en `/docs`.

---

## Pruebas

Los tests usan **SQLite en memoria** (no requieren MySQL). Se ejecutan con `pytest`:

```bash
# Todas las pruebas
pytest

# Con cobertura
pytest --cov=app --cov-report=term --cov-report=xml

# Ver reporte HTML
pytest --cov=app --cov-report=html
```

Requiere: `pytest`, `pytest-cov`, `httpx`.

---

## Análisis con SonarQube

SonarQube corre localmente en Docker:

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
```

Escaneo con cobertura (después de generar `coverage.xml`):

```bash
pysonar --sonar-host-url http://localhost:9000 \
        --token <token> \
        --sonar-project-key Filmate-Backend \
        --sonar-sources app \
        --sonar-tests tests \
        --coverage-report-paths coverage.xml
```

---

## Endpoints

### Auth

| Ruta | Método | Descripción |
|---|---|---|
| `/auth/register` | POST | Registro de usuario |
| `/auth/login` | POST | Inicio de sesión |

### Legacy / público (sin prefijo `/client`)

Routers previos a la separación cliente/admin, todavía montados en `create_app()`. El grueso de la app (y todo lo nuevo) vive bajo `/client/...` — ver la siguiente sección.

| Ruta | Método | Descripción |
|---|---|---|
| `/users/{user_id}` | GET / PUT | Perfil de usuario |
| `/users/search` | GET | Buscar usuarios |
| `/movies/` , `/movies/{id}` | GET | Catálogo de películas |
| `/cinemas/` , `/cinemas/{id}` | GET | Cines |
| `/showtimes/cinema/{id}` , `/showtimes/movie/{id}` | GET | Funciones |
| `/seats/showtime/{id}` , `/seats/lock` | GET / POST | Mapa y bloqueo de asientos |
| `/orders/checkout` | POST | Checkout (versión legacy, sin pasarela de pago) |
| `/reservations/user/{id}` , `/reservations/{id}` | GET | Historial de transacciones |
| `/interacciones/` | POST / GET | Interacciones película-usuario |
| `/ws/seats/{showtime_id}` | WS | Tiempo real del mapa de asientos |

### Cliente (prefijo `/client/...`)

Superficie principal de la API para la app de usuario final. Ninguna de estas rutas valida autenticación real todavía (reciben `user_id`/`id_usuario` como parámetro).

**Películas** (`client_movies.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/movies/` | GET | Lista con filtros: `genero_id`, `clasificacion`, `anio_lanzamiento`, `estado_pelicula`, `order_by` (`titulo_asc/desc`, `anio_asc/desc`, `recientes`) |
| `/client/movies/search?q=` | GET | Búsqueda por título/sinopsis |
| `/client/movies/{id}` | GET | Detalle básico |
| `/client/movies/{id}/details?viewer_id=` | GET | Detalle completo (promedio, géneros); con `viewer_id` incluye `mi_calificacion`, `es_favorita`, `vista_por_mi` |
| `/client/movies/available/by-datetime` | GET | Películas con función en un rango de fecha/hora |

**Reseñas** (`client_reviews.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/reviews/` | POST | Crear/actualizar reseña (una sola por usuario+película) |
| `/client/reviews/{id}` | GET / PUT / DELETE | Detalle (con `total_comentarios`, likes), editar, borrar |
| `/client/reviews/movie/{id}?viewer_id=` | GET | Reseñas de una película |
| `/client/reviews/user/{id}` | GET | Reseñas de un usuario |
| `/client/reviews/following/{id}` | GET | Reseñas de las cuentas seguidas |
| `/client/reviews/user/{id}/rating-distribution` | GET | Distribución de estrellas 1–5 |
| `/client/reviews/user/{id}/movies` | GET | Películas calificadas por el usuario |
| `/client/reviews/{id}/toggle-like` | POST | Dar/quitar like |
| `/client/reviews/{id}/comments` | GET / POST | Listar / agregar comentarios a una reseña |
| `/client/reviews/{id}/comments/{comment_id}` | DELETE | Borrar comentario propio |

**Interacciones (favoritos / vistas)** (`client_interacciones.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/interacciones/` | POST | Upsert de favorita/vista/watchlist |
| `/client/interacciones/usuario/{id}` | GET | Interacciones de un usuario |
| `/client/interacciones/usuario/{id}/pelicula/{id}` | GET / DELETE | Interacción puntual |
| `/client/interacciones/usuario/{id}/pelicula/{id}/toggle-vista` | POST | Alterna visto/no-visto en un solo click |
| `/client/interacciones/usuario/{id}/vistas/count` | GET | Total de películas vistas |

**Perfil / favoritos** (`client_users.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/users/{id}/favorite-movies?genero_id=` | GET | Películas favoritas (con fecha en que se marcaron) |
| `/client/users/{id}/favorite-movies/count` | GET | Total de favoritas |
| `/client/users/{id}/favorite-movies` | PUT | Definir el top-5 de destacadas |
| `/client/users/{id}/purchases` | GET | Historial de compras |

**Social / feed de actividad** (`client_social.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/social/feed` | GET | Feed global (últimos 50 eventos) |
| `/client/social/activity/{id}` | GET | Actividad de un usuario |
| `/client/social/following-activity/{id}` | GET | Actividad de las cuentas seguidas |
| `/client/social/summary/{id}` | GET | Perfil + stats + top-5 destacadas |
| `/client/social/profile/{id}` | PUT | Actualizar bio |
| `/client/social/{activity_id}` | DELETE | Borrar un evento |

**Seguidores** (`client_seguidores.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/seguidores/seguir` , `/dejar-de-seguir` | POST | Seguir / dejar de seguir |
| `/client/seguidores/{id}/seguidores` , `/{id}/siguiendo` | GET | Listas de seguidores/seguidos |
| `/client/seguidores/{id}/counts` | GET | Conteos |
| `/client/seguidores/check/{a}/sigue-a/{b}` | GET | Chequeo puntual |

**Colecciones / carrito / snacks** (`client_colecciones.py`, `client_carrito.py`, `client_snacks.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/colecciones/usuario/{id}` | GET | Colecciones del usuario |
| `/client/colecciones/` | POST | Crear colección |
| `/client/colecciones/agregar-pelicula` | POST | Agregar película a colección |
| `/client/colecciones/{id}/pelicula/{pid}` | DELETE | Quitar película |
| `/client/carrito/{user_id}` | GET | Carrito del usuario |
| `/client/carrito/` , `/{id}` | POST / PUT / DELETE | Gestionar ítems del carrito |
| `/client/snacks/categories` , `/products` | GET | Catálogo de confitería |
| `/client/snacks/cart/calculate` | POST | Calcular subtotal de confitería |

**Cines / salas / funciones / asientos** (`client_cinemas.py`, `client_rooms.py`, `client_showtimes.py`, `client_seats.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/cinemas/` , `/{id}` | GET | Cines |
| `/client/rooms/` , `/{id}` | GET | Salas |
| `/client/showtimes/cinema/{id}` , `/movie/{id}` , `/date/{d}` , `/range` | GET | Funciones disponibles |
| `/client/seats/showtime/{id}` | GET | Mapa de asientos |
| `/client/seats/lock` | POST | Bloquear asientos (10 min) |

**Compra y pagos** (`client_orders.py`, `client_payments.py`, `client_tickets.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/payments/metodos-prueba` | GET | Catálogo de tarjetas/Yape de prueba (ver [Pasarela de pagos](#pasarela-de-pagos-simulada)) |
| `/client/payments/tokenize/tarjeta` | POST | Tokeniza una tarjeta de prueba |
| `/client/payments/tokenize/yape` | POST | Tokeniza un pago Yape de prueba (requiere OTP) |
| `/client/orders/checkout` | POST | Cierra la compra: cobra el `token_pago`, marca asientos, genera tickets |
| `/client/tickets/issue` | POST | Emitir ticket |
| `/client/tickets/transaction/{id}` | GET | Detalle de transacción |
| `/client/tickets/transaction/{id}/pdf` | GET | Ticket en PDF con QR |

**Reembolsos y reservas** (`client_reembolsos.py`, `client_reservations.py`)

| Ruta | Método | Descripción |
|---|---|---|
| `/client/reembolsos/` | POST | Solicitar reembolso |
| `/client/reembolsos/mis-solicitudes` | GET | Mis solicitudes |
| `/client/reservations/user/{id}` , `/{id}` | GET | Historial y detalle de compras |

### Administración (prefijo `/admin/`)

| Ruta | Método | Descripción |
|---|---|---|
| `/admin/movies/` | GET | Listar películas (admin) |
| `/admin/movies/` | POST | Crear película |
| `/admin/movies/{id}` | PUT | Actualizar película |
| `/admin/movies/{id}` | DELETE | Eliminar película (soft) |
| `/admin/movies/meta/genres` | GET | Listar géneros |
| `/admin/movies/tmdb/search` | GET | Buscar películas en TMDb |
| `/admin/movies/tmdb/{id}/preview` | GET | Vista previa con datos de TMDb |
| `/admin/movies/tmdb/{id}` | POST | Crear película desde TMDb (auto-rellena todo) |
| `/admin/movies/meta/categories` | GET | Listar categorías |
| `/admin/movies/meta/classifications` | GET | Listar clasificaciones |
| `/admin/cinemas/` | GET | Listar cines |
| `/admin/cinemas/` | POST | Crear cine |
| `/admin/cinemas/{id}` | PUT | Actualizar cine |
| `/admin/cinemas/{id}` | DELETE | Desactivar cine |
| `/admin/rooms/` | GET | Listar salas |
| `/admin/rooms/` | POST | Crear sala |
| `/admin/rooms/{id}` | GET | Detalle de sala |
| `/admin/rooms/{id}` | PUT | Actualizar sala |
| `/admin/rooms/{id}` | DELETE | Desactivar sala |
| `/admin/showtimes/` | GET | Listar funciones |
| `/admin/showtimes/` | POST | Crear función |
| `/admin/showtimes/{id}` | PUT | Actualizar función |
| `/admin/showtimes/{id}` | DELETE | Eliminar función |
| `/admin/seats/room/{id}` | GET | Asientos por sala |
| `/admin/seats/room/{id}/bulk` | POST | Crear asientos en lote |
| `/admin/seats/{id}` | PUT | Actualizar asiento |
| `/admin/seats/{id}` | DELETE | Desactivar asiento |
| `/admin/users/` | GET | Listar usuarios |
| `/admin/users/` | POST | Crear usuario |
| `/admin/transactions/` | GET | Transacciones con filtros |
| `/admin/transactions/{id}` | GET | Detalle de transacción |
| `/admin/transactions/validate` | POST | Validar ticket QR |
| `/admin/reembolsos/` | GET | Solicitudes de reembolso |
| `/admin/reembolsos/{id}` | GET | Detalle de solicitud |
| `/admin/reembolsos/{id}` | PUT | Aprobar/rechazar reembolso |
| `/admin/reembolsos/metricas` | GET | Métricas de reembolsos |
| `/admin/reservations/` | GET | Listado global de transacciones |
| `/admin/roles/` | GET | Roles del sistema |
| `/admin/roles/{id}/permisos` | GET | Permisos de un rol |

---

## Pasarela de pagos (simulada)

`app/services/payment_gateway_service.py` implementa una pasarela de pago **simulada en memoria**, sin llamar a ningún proveedor externo (Culqi/Mercado Pago/Izipay quedaron descartados para este proyecto por requerir RUC o presentar problemas de sandbox). No necesita configuración en `.env`.

Flujo: tokenizar → checkout. El `token` es de un solo uso (se invalida al cobrarlo).

1. `GET /client/payments/metodos-prueba` — devuelve el catálogo vigente de tarjetas y números Yape de prueba.
2. `POST /client/payments/tokenize/tarjeta` o `/tokenize/yape` — valida los datos contra el catálogo y devuelve un `token`.
3. `POST /client/orders/checkout` con `{ ..., "token_pago": "<token>", "email": "..." }` — cobra el token; si el resultado simulado es de rechazo, responde `402` y no toca los asientos.

**Tarjetas de prueba:**

| Número | Marca | CVV | Vencimiento | Resultado |
|---|---|---|---|---|
| 4551 7000 0000 0004 | Visa | 123 | 11/30 | Aprobado |
| 5301 7000 0000 0006 | Mastercard | 123 | 11/30 | Aprobado |
| 4551 7000 0000 0012 | Visa | 123 | 11/30 | Fondos insuficientes |
| 4551 7000 0000 0020 | Visa | 123 | 11/30 | Tarjeta inválida |
| 4551 7000 0000 0038 | Visa | 123 | 11/30 | Tarjeta vencida |

**Yape de prueba** (requiere código OTP `123456`):

| Celular | Resultado |
|---|---|
| 999111222 | Aprobado |
| 999111000 | Fondos insuficientes |

Para volver a un proveedor real en el futuro, solo hace falta reemplazar la lógica interna de `payment_gateway_service.cobrar(...)` — `order_service.py` y el contrato de `/client/orders/checkout` (`token_pago` + `email`) ya están pensados para eso.

---

## Base de datos

Esquema en `scripts/DSOOMDAG4v2.3.sql` — 31 tablas con modelos, vistas, triggers y procedimientos almacenados. No hay migraciones (Alembic u otra herramienta): los cambios de esquema se hacen editando este script a mano.

Módulos principales:
- **Seguridad**: `usuarios`, `roles`, `permisos`, `usuarios_roles`, `roles_permisos`
- **Catálogo**: `peliculas`, `generos`, `peliculas_generos`
- **Infraestructura**: `cines`, `salas`, `asientos`
- **Programación**: `funciones`, `asientos_funciones`
- **Ventas**: `transacciones`, `boletas_ticket`, `detalles_boleta_asiento`, `detalles_boleta_confiteria`
- **Confitería**: `categorias_confiteria`, `productos_confiteria`
- **Comunidad**: `resenas`, `interacciones_peliculas`, `colecciones`, `colecciones_peliculas`, `seguidores`, `historial_actividad`
- **Reembolsos**: `solicitudes_reembolso`, `detalles_reembolso`
- **Bloqueos**: `bloqueos_temporales`

---

## Dependencias principales

| Librería | Uso |
|---|---|
| fastapi | Framework |
| uvicorn | Servidor ASGI |
| sqlalchemy | ORM |
| pymysql | Conector MySQL |
| pydantic | Validación |
| httpx | Cliente HTTP (API TMDb, tests) |
| reportlab | PDF |
| qrcode[pil] | QR |
| python-dotenv | Variables de entorno |

---

## Herramientas de desarrollo

| Herramienta | Uso |
|---|---|
| pytest + pytest-cov | Pruebas y cobertura |
| httpx | Cliente HTTP para tests |
| pysonar | Escáner de SonarQube |
| ruff | Linter |

---

## Scripts útiles

```bash
uvicorn app.main:app --reload --port 8001
uvicorn app.main:app --host 0.0.0.0 --port 8000
pytest --cov=app --cov-report=term
pysonar --sonar-host-url http://localhost:9000 --token <token> --sonar-project-key Filmate-Backend --sonar-sources app --sonar-tests tests --coverage-report-paths coverage.xml
```
