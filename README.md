# 🎬 Filmate — Backend API

API REST para la plataforma de cine **Filmate**, construida con **FastAPI** y **SQLAlchemy**. Gestiona catálogo de películas, funciones, reservas, boletos, dulcería y validación de entradas en tiempo real.

---

## 📁 Estructura del Proyecto

```
backend/
├── alembic/                  # Migraciones de la base de datos
├── app/
│   ├── core/                 # Configuración, seguridad y constantes
│   ├── models/               # Modelos ORM (tablas de la BD)
│   ├── repositories/         # Capa de acceso a datos
│   ├── routes/               # Endpoints de la API
│   ├── schemas/              # Esquemas de validación (Pydantic)
│   ├── services/             # Lógica de negocio
│   ├── utils/                # Funciones auxiliares (PDF, QR, etc.)
│   ├── websocket/            # Conexiones en tiempo real
│   └── main.py               # Punto de entrada de la aplicación
├── docs/
│   ├── source/               # Fuentes de documentación
│   ├── requirements-docs.txt
│   ├── swagger.md
│   └── USO_DOCS.md
├── scripts/
│   ├── build_docs.py         # Script para compilar la documentación
│   └── DSOOMDAG4v1.5.sql     # Script de la base de datos
├── .env                      # Variables de entorno
├── requirements.txt          # Dependencias de Python
└── README.md
```

---

## ⚙️ Requisitos previos

- Python **3.11+**
- MySQL **8.0+**
- pip

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/filmate-backend.git  #o en su defecto la rama develop que tambien es donde estan las actualizaciones aprobadas (recomiendo esa)
cd filmate-backend/backend
```

### 2. Crear y activar el entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz de `backend/` con el siguiente contenido:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=admin
DB_NAME=filmate_db
```

### 5. Inicializar la base de datos

Ejecuta los scripts SQL en MySQL en este orden:

```bash
# 1. Crear esquema y tablas
mysql -u root -p < scripts/init_db.sql

# 2. Insertar datos de prueba
mysql -u root -p < scripts/seeds.sql
```

O desde MySQL Workbench / DBeaver, ejecuta ambos archivos manualmente.

---

## ▶️ Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en: `http://localhost:8000`

---

## 📖 Documentación de la API

Una vez que el servidor esté corriendo, accede a:

| Interfaz | URL |
|---|---|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

---

## 🔌 Endpoints principales

| Módulo | Prefijo | Descripción |
|---|---|---|
| Películas | `/movies` | CRUD de catálogo, géneros, clasificaciones |
| Funciones | `/showtimes` | Programación de funciones por sala |
| Reservas | `/orders` | Checkout y generación de boletos |
| Ventas | `/api/ventas` | Historial, detalle y métricas de transacciones |
| Tickets | `/tickets` | Consulta y descarga de tickets en PDF |
| Snacks | `/snacks` | Catálogo de dulcería y cálculo de carrito |
| Usuarios | `/users` | Registro y consulta de usuarios |

---

## 🗄️ Base de datos

El proyecto usa **MySQL** con **SQLAlchemy** como ORM. El esquema incluye los siguientes módulos:

- **Seguridad** — roles y usuarios
- **Catálogo** — películas, géneros, actores, banners
- **Infraestructura** — cines, salas y asientos
- **Programación** — funciones y tarifas
- **Ventas** — reservas, boletos, promociones
- **Dulcería** — categorías y productos snack
- **Comunidad** — reseñas y favoritos

---

## 🧪 Datos de prueba

El archivo `scripts/seeds.sql` incluye:

- 2 usuarios (1 admin, 1 cliente)
- 3 películas con géneros y actores
- 1 cine con 2 salas y asientos
- 2 funciones programadas
- 1 reserva de ejemplo con boletos y dulcería
- Tarifas y una promoción activa

---

## 📦 Dependencias principales

| Librería | Versión | Uso |
|---|---|---|
| `fastapi` | 0.136.1 | Framework principal |
| `uvicorn` | 0.47.0 | Servidor ASGI |
| `sqlalchemy` | 2.0.49 | ORM |
| `pydantic` | 2.13.4 | Validación de datos |
| `PyMySQL` | 1.2.0 | Conector MySQL |
| `python-dotenv` | 1.2.2 | Variables de entorno |
| `reportlab` | latest | Generación de PDFs |
| `qrcode[pil]` | latest | Generación de códigos QR |

---

## 🔧 Scripts útiles

```bash
# Generar documentación Sphinx
python scripts/build_docs.py

# Ejecutar con puerto personalizado
uvicorn app.main:app --reload --port 8001

# Ejecutar en producción (sin reload)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📝 Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DB_HOST` | Host de la base de datos | `localhost` |
| `DB_PORT` | Puerto MySQL | `3306` |
| `DB_USER` | Usuario MySQL | `root` |
| `DB_PASSWORD` | Contraseña MySQL | `admin` |
| `DB_NAME` | Nombre de la base de datos | `filmate_db` |

---

## 🤝 Contribuir

1. Crea un fork del repositorio
2. Crea tu rama: `git checkout -b feature/nueva-funcionalidad`
3. Haz commit de tus cambios: `git commit -m 'feat: descripción'`
4. Push a tu rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto fue desarrollado como proyecto universitario. Todos los derechos reservados.