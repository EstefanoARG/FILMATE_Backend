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
│   └── DSOOMDAG4v2.1.sql  # Esquema de base de datos
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
```

Ejecutar el script SQL en MySQL:

```bash
mysql -u root -p < scripts/DSOOMDAG4v2.1.sql
```

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

### Usuario (público / cliente)

| Ruta | Método | Descripción |
|---|---|---|
| `/auth/register` | POST | Registro de usuario |
| `/auth/login` | POST | Inicio de sesión |
| `/users/{user_id}` | GET | Perfil de usuario |
| `/users/{user_id}` | PUT | Actualizar perfil |
| `/users/search` | GET | Buscar usuarios |
| `/movies/` | GET | Listar películas |
| `/movies/{id}` | GET | Detalle de película |
| `/movies/{id}/details` | GET | Detalle completo (con géneros, reparto) |
| `/cinemas/` | GET | Listar cines |
| `/cinemas/{id}` | GET | Detalle de cine |
| `/showtimes/cinema/{id}` | GET | Funciones por cine |
| `/showtimes/movie/{id}` | GET | Funciones por película |
| `/seats/showtime/{id}` | GET | Mapa de asientos por función |
| `/seats/lock` | POST | Bloquear asientos temporalmente |
| `/orders/checkout` | POST | Procesar compra completa |
| `/tickets/transaction/{id}` | GET | Detalle de transacción |
| `/tickets/transaction/{id}/pdf` | GET | Descargar ticket en PDF |
| `/tickets/issue` | POST | Emitir ticket |
| `/reviews/` | POST | Crear reseña |
| `/reviews/movie/{id}` | GET | Reseñas de una película |
| `/reviews/{id}` | DELETE | Eliminar reseña |
| `/snacks/categories` | GET | Categorías de confitería |
| `/snacks/products` | GET | Productos de confitería |
| `/snacks/cart/calculate` | POST | Calcular carrito |
| `/reembolsos/` | POST | Solicitar reembolso |
| `/reembolsos/mis-solicitudes` | GET | Mis solicitudes de reembolso |
| `/reservations/user/{id}` | GET | Historial de transacciones |
| `/reservations/{id}` | GET | Detalle de transacción |
| `/interacciones/` | POST | Like/favorito a película |
| `/interacciones/usuario/{id}` | GET | Interacciones del usuario |
| `/colecciones/` | POST | Crear colección |
| `/colecciones/usuario/{id}` | GET | Colecciones del usuario |
| `/colecciones/agregar-pelicula` | POST | Agregar película a colección |
| `/colecciones/{col_id}/pelicula/{pel_id}` | DELETE | Quitar película de colección |
| `/carrito/{user_id}` | GET | Carrito del usuario |
| `/carrito/` | POST | Agregar item al carrito |
| `/carrito/{id}` | PUT | Actualizar item |
| `/carrito/{id}` | DELETE | Eliminar item |
| `/seguidores/seguir` | POST | Seguir usuario |
| `/seguidores/dejar-de-seguir` | POST | Dejar de seguir |
| `/seguidores/{id}/seguidores` | GET | Lista de seguidores |
| `/seguidores/{id}/siguiendo` | GET | Lista de seguidos |
| `/actividad/feed` | GET | Feed de actividad social |
| `/actividad/usuario/{id}` | GET | Actividad de un usuario |
| `/ws/seats/{showtime_id}` | WS | Tiempo real del mapa de asientos |

### Administración (prefijo `/admin/`)

| Ruta | Método | Descripción |
|---|---|---|
| `/admin/movies/` | GET | Listar películas (admin) |
| `/admin/movies/` | POST | Crear película |
| `/admin/movies/{id}` | PUT | Actualizar película |
| `/admin/movies/{id}` | DELETE | Eliminar película (soft) |
| `/admin/movies/meta/genres` | GET | Listar géneros |
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

## Base de datos

Esquema en `scripts/DSOOMDAG4v2.1.sql` — 31 tablas con modelos, vistas, triggers y procedimientos almacenados.

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
