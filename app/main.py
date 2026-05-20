"""API principal de Filmate.

Este módulo define la instancia de `FastAPI`, registra las rutas principales
y expone endpoints básicos de salud y estado. Los `tags_metadata` se usan
para mejorar la documentación automática (OpenAPI / Swagger).
"""

from fastapi import FastAPI
import logging

from app.core.database import engine, Base
from app.models import *
from app.routes import movies, users, reviews

logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "users", "description": "Operaciones sobre usuarios (registro, consulta)."},
    {"name": "movies", "description": "Catálogo de películas: listado, creación y detalles."},
    {"name": "reviews", "description": "Gestión de reseñas: creación y listado por película."},
]

app = FastAPI(
    title="Filmate API",
    version="0.1.0",
    description="API para la plataforma Filmate. Documentación disponible en Swagger UI.",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(movies.router)
app.include_router(reviews.router)


@app.get("/", summary="Estado del servicio")
def root():
    """Endpoint raíz que devuelve un mensaje simple indicando que la API está activa.

    Se utiliza para comprobaciones rápidas y para proporcionar un punto de entrada
    legible en la documentación.
    """
    logger.info("✅ GET / - API activa")
    return {"message": "Filmate API funcionando"}


@app.get("/health", summary="Health Check - Verifica conexión a BD", tags=["health"])
def health_check():
    """Endpoint para verificar si la API y la BD están funcionando."""
    logger.info("🏥 GET /health - Verificando estado")
    try:
        with engine.connect() as conn:
            logger.info("✅ Health check: BD conectada")
            return {
                "status": "healthy",
                "database": "connected"
            }
    except Exception as e:
        logger.error(f"❌ Health check falló: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }