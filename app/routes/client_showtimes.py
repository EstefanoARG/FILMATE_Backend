import logging
from datetime import date
from typing import Annotated, List
from datetime import datetime
from app.core.dependencies import get_db
from app.models.showtime import Funcion
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.showtime import CinemaShowtimesResponse, ShowtimeResponse
from app.services.showtime_service import list_showtimes_by_cinema, list_showtimes_by_movie, list_showtimes_by_date

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/showtimes", tags=["client showtimes"])

@router.get("/cinema/{cinema_id}", response_model=CinemaShowtimesResponse)
def get_showtimes_by_cinema(cinema_id: int, db: Annotated[Session, Depends(get_db)]):
    logger.info("GET /client/showtimes/cinema/%s", cinema_id)
    return list_showtimes_by_cinema(db, cinema_id)

@router.get("/movie/{movie_id}", responses={500: {"description": "Internal server error"}})
def get_showtimes_by_movie(movie_id: int, db: Annotated[Session, Depends(get_db)]):
    logger.info("GET /client/showtimes/movie/%s", movie_id)
    try:
        return list_showtimes_by_movie(db, movie_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Error en GET /client/showtimes/movie/%s", movie_id)
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/date/{target_date}", response_model=List[ShowtimeResponse], responses={500: {"description": "Internal server error"}})
def get_showtimes_by_date(
    target_date: date,
    db: Annotated[Session, Depends(get_db)],
    cinema_id: int | None = None,
    movie_id: int | None = None,
):
    logger.info("GET /client/showtimes/date/%s", target_date)
    try:
        return list_showtimes_by_date(db, target_date=target_date, cinema_id=cinema_id, movie_id=movie_id)
    except Exception as exc:
        logger.exception("Error en GET /client/showtimes/date/%s", target_date)
        raise HTTPException(status_code=500, detail=str(exc))
    
@router.get("/range", response_model=List[ShowtimeResponse])
def get_showtimes_by_datetime_range(
    start_datetime: Annotated[datetime, Query(description="Fecha y hora de inicio (Ej: 2026-06-10T14:00:00)")],
    end_datetime: Annotated[datetime, Query(description="Fecha y hora de fin (Ej: 2026-06-10T23:59:59)")],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Retorna todas las funciones programadas dentro de un rango exacto de fecha y hora.
    """
    funciones = (
        db.query(Funcion)
        .filter(
            Funcion.fecha_hora >= start_datetime,
            Funcion.fecha_hora <= end_datetime
        )
        .order_by(Funcion.fecha_hora.asc())
        .all()
    )
    return funciones