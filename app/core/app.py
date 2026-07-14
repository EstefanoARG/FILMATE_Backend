from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import logging

from app.core.database import engine
import app.models
from app.routes import (
    auth, cinemas, movies, users, showtimes, seats, orders,
    client_movies, client_cinemas, client_showtimes, client_seats,
    client_orders, client_tickets, client_reviews, client_snacks, client_payments,
    client_reservations, client_interacciones,
    client_colecciones, client_carrito, client_seguidores, client_social,
    client_rooms, client_users, client_reembolsos,
    admin_movies, admin_cinemas, admin_showtimes, admin_seats, admin_users,
    admin_transactions, rooms, admin_reembolsos,
    reservations, admin_reservas, interacciones, roles, admin_dashboard,
    admin_reports, admin_config, permisos, admin_logs,
    admin_notifications,
)
from app.websocket.seats_ws import router as seats_ws_router

logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "auth", "description": "Registro y autenticación."},
    {"name": "users", "description": "Perfil de usuario."},
    {"name": "movies", "description": "Catálogo de películas (público)."},
    {"name": "cinemas", "description": "Listado de cines (público)."},
    {"name": "showtimes", "description": "Funciones y horarios (público)."},
    {"name": "seats", "description": "Mapa y bloqueo de asientos (público)."},
    {"name": "orders", "description": "Cierre de compra."},
    {"name": "tickets", "description": "Emisión de tickets y QR."},
    {"name": "reservations", "description": "Historial de transacciones (usuario)."},
    {"name": "interacciones", "description": "Interacciones con películas."},
    {"name": "admin movies", "description": "Admin: CRUD de películas y metadatos."},
    {"name": "admin cinemas", "description": "Admin: CRUD de cines."},
    {"name": "admin rooms", "description": "Admin: CRUD de salas."},
    {"name": "admin showtimes", "description": "Admin: CRUD de funciones."},
    {"name": "admin seats", "description": "Admin: gestión de asientos por sala."},
    {"name": "admin users", "description": "Admin: listar/crear usuarios."},
    {"name": "admin reembolsos", "description": "Admin: revisar y resolver reembolsos."},
    {"name": "admin reservations", "description": "Admin: listado de transacciones."},
    {"name": "admin transactions", "description": "Admin: ventas y validación de tickets."},
    {"name": "admin roles", "description": "Admin: roles y permisos del sistema."},
    {"name": "admin dashboard", "description": "Admin: métricas agregadas del dashboard."},
    {"name": "admin reports", "description": "Admin: reportes de taquilla, ocupación, ventas y análisis."},
    {"name": "admin notifications", "description": "Admin: notificaciones del sistema."},
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="Filmate API",
        version="0.2.0",
        description="API para la plataforma Filmate — Nueva BD",
        openapi_tags=tags_metadata,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # Los frontends viven en Vercel (dominio de producción fijo + subdominios
    # de preview dinámicos por deploy) y se conectan directo a este backend.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(cinemas.router)
    app.include_router(movies.router)
    app.include_router(showtimes.router)
    app.include_router(seats.router)
    app.include_router(orders.router)
    app.include_router(seats_ws_router)
    app.include_router(reservations.router)
    app.include_router(interacciones.router)

    app.include_router(client_movies.router)
    app.include_router(client_cinemas.router)
    app.include_router(client_showtimes.router)
    app.include_router(client_seats.router)
    app.include_router(client_orders.router)
    app.include_router(client_payments.router)
    app.include_router(client_tickets.router)
    app.include_router(client_snacks.router)
    app.include_router(client_reservations.router)
    app.include_router(client_interacciones.router)
    app.include_router(client_colecciones.router)
    app.include_router(client_carrito.router)
    app.include_router(client_seguidores.router)
    app.include_router(client_social.router)
    app.include_router(client_reviews.router)
    app.include_router(client_rooms.router)
    app.include_router(client_users.router)
    app.include_router(client_reembolsos.router)

    app.include_router(admin_movies.router)
    app.include_router(admin_cinemas.router)
    app.include_router(admin_showtimes.router)
    app.include_router(admin_seats.router)
    app.include_router(admin_users.router)
    app.include_router(rooms.router)
    app.include_router(roles.router)
    app.include_router(admin_transactions.router)
    app.include_router(admin_reembolsos.router)
    app.include_router(admin_reservas.router)
    app.include_router(admin_dashboard.router)
    app.include_router(admin_reports.router)
    app.include_router(admin_config.router)
    app.include_router(admin_logs.router)
    app.include_router(permisos.router)
    app.include_router(admin_notifications.router)

    @app.get("/", summary="Estado del servicio")
    def root():
        logger.info("GET / - API activa")
        return {"message": "Filmate API funcionando"}

    @app.get("/docs", include_in_schema=False)
    def docs_redirect():
        return RedirectResponse(url="/api/docs")

    @app.get("/redoc", include_in_schema=False)
    def redoc_redirect():
        return RedirectResponse(url="/api/redoc")

    @app.get("/health", summary="Health Check", tags=["health"])
    def health_check():
        logger.info("GET /health - Verificando estado")
        try:
            with engine.connect():
                logger.info("Health check: BD conectada")
                return {"status": "healthy", "database": "connected"}
        except Exception as e:
            logger.exception("Health check falló")
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

    return app
