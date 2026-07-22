"""Configuración de la base de datos.

Este módulo crea el `engine`, `SessionLocal` y `Base` para SQLAlchemy.
Por seguridad y para evitar efectos colaterales durante la generación de
documentación automática, la conexión a la base de datos puede fallar si las
variables de entorno no están definidas; en `conf.py` de Sphinx marcamos
estas dependencias en `autodoc_mock_imports` para evitar que la importación
ejecute lógica de conexión.

Variables exportadas:
- `engine`: motor SQLAlchemy (puede lanzar si las variables de entorno faltan).
- `SessionLocal`: fábrica de sesiones.
- `Base`: clase base declarativa para modelos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Lee configuración de la BD desde variables de entorno
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

skip_connect = os.getenv("SKIP_DB_CONNECT", "0").lower() in ("1", "true", "yes")
missing_db_config = not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME])

logger.info(f"🔗 Conectando a BD: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

if skip_connect and missing_db_config:
    DATABASE_URL = "sqlite:///:memory:"
    logger.info("Usando SQLite en memoria para pruebas sin conexion a BD")

# Crear el engine sin forzar la conexión. Algunas herramientas (p. ej. Sphinx)
# importan los módulos del paquete; evitar probar la conexión en el import
# previene bloqueos o fallos durante la generación de la documentación.
engine = create_engine(DATABASE_URL, echo=True, connect_args={
    "init_command": "SET time_zone = '+00:00'"
})

# Por defecto intentamos una comprobación de conexión, pero permitimos omitirla
# estableciendo la variable de entorno `SKIP_DB_CONNECT` (útil para docs/CI).
skip_connect = os.getenv("SKIP_DB_CONNECT", "0").lower() in ("1", "true", "yes")
if not skip_connect:
    try:
        with engine.connect() as conn:
            logger.info("✅ Conexión a BD exitosa")
    except Exception as e:
        # En entornos de documentación o CI la conexión puede fallar; registramos el error
        logger.exception("❌ Error al conectar a BD")

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
