import logging
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.showtime import CinemaShowtimesResponse, ShowtimeResponse
from app.services.showtime_service import list_showtimes_by_cinema, list_showtimes_by_movie, list_showtimes_by_date

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/showtimes", tags=["showtimes"])


@router.get("/cinema/{cinema_id}", response_model=CinemaShowtimesResponse)
def get_showtimes_by_cinema(cinema_id: int, db: Session = Depends(get_db)):
    logger.info("GET /showtimes/cinema/%s", cinema_id)
    return list_showtimes_by_cinema(db, cinema_id)


@router.get("/movie/{movie_id}")
def get_showtimes_by_movie(movie_id: int, db: Session = Depends(get_db)):
    logger.info("GET /showtimes/movie/%s", movie_id)
    try:
        return list_showtimes_by_movie(db, movie_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error en GET /showtimes/movie/%s: %s", movie_id, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/date/{target_date}", response_model=List[ShowtimeResponse])
def get_showtimes_by_date(
    target_date: date,
    cinema_id: int | None = None,
    movie_id: int | None = None,
    db: Session = Depends(get_db),
):
    logger.info("GET /showtimes/date/%s", target_date)
    try:
        return list_showtimes_by_date(db, target_date=target_date, cinema_id=cinema_id, movie_id=movie_id)
    except Exception as exc:
        logger.error("Error en GET /showtimes/date/%s: %s", target_date, exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))
