"""Endpoint del Motor de Recomendación Inteligente (RF F-03 / HU-SOC-04)."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation_service import get_personalized_recommendations

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/recommendations",
    tags=["recommendations"],
    responses={
        401: {"description": "Token requerido o inválido"},
        500: {"description": "Error al calcular recomendaciones"},
    },
)


@router.get(
    "/home",
    response_model=RecommendationResponse,
    summary="Recomendaciones personalizadas para el carrusel de inicio",
)
async def recommendations_home(
    payload: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50, description="Cantidad máxima de sugerencias"),
):
    """Devuelve películas recomendadas para el usuario autenticado.

    El algoritmo cruza tres señales del usuario:
      1. Películas marcadas como favoritas.
      2. Directores de películas calificadas con 5 estrellas.
      3. Géneros con mayor número de compras (transacciones).

    Excluye películas ya marcadas como favoritas o vistas y devuelve un
    ranking por score de relevancia.
    """
    user_id = int(payload.get("user_id"))
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Token sin user_id válido")

    logger.info("GET /api/recommendations/home user_id=%s limit=%s", user_id, limit)
    try:
        return await get_personalized_recommendations(user_id, limit=limit, db=db)
    except Exception as exc:
        logger.exception("Fallo calculando recomendaciones user_id=%s", user_id)
        raise HTTPException(
            status_code=500,
            detail="No fue posible calcular las recomendaciones",
        ) from exc
