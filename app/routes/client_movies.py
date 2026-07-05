import logging
from typing import List, Optional, Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.dependencies import get_db
from app.repositories import movie_repository
from app.schemas.movie import MovieResponse, MovieDetailsResponse
from app.services.movie_service import get_movie_details
from app.models.movie import Pelicula
from app.models.showtime import Funcion

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/movies", tags=["client movies"])

@router.get("/", response_model=List[MovieResponse])
def list_movies(
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 50,
    genero_id: Optional[int] = None,
    clasificacion: Optional[str] = None,
    anio_lanzamiento: Optional[int] = None,
    estado_pelicula: Optional[str] = None,
    order_by: Optional[str] = Query(None, description="titulo_asc, titulo_desc, anio_asc, anio_desc, recientes"),
):
    return movie_repository.list_movies(
        db,
        skip=skip,
        limit=limit,
        genero_id=genero_id,
        clasificacion=clasificacion,
        anio_lanzamiento=anio_lanzamiento,
        estado_pelicula=estado_pelicula,
        order_by=order_by,
    )

@router.get("/search", response_model=List[MovieResponse])
def search_movies(q: Annotated[str, Query()], db: Annotated[Session, Depends(get_db)]):
    """Busca películas por título o sinopsis desde el backend sin cargar todas al front."""
    peliculas = (
        db.query(Pelicula)
        .filter(
            or_(
                Pelicula.titulo.ilike(f"%{q}%"),
                Pelicula.sinopsis.ilike(f"%{q}%")
            ),
            Pelicula.eliminado == False
        )
        .limit(20)
        .all()
    )
    return peliculas

@router.get("/{movie_id}", response_model=MovieResponse, responses={404: {"description": "Movie not found"}})
def get_movie(movie_id: int, db: Annotated[Session, Depends(get_db)]):
    movie = movie_repository.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.get("/{movie_id}/details", response_model=MovieDetailsResponse)
def movie_details(movie_id: int, db: Annotated[Session, Depends(get_db)], viewer_id: Optional[int] = None):
    return get_movie_details(db, movie_id, viewer_id)

@router.get("/available/by-datetime", response_model=List[MovieResponse])
def get_movies_by_datetime_range(
    start_datetime: Annotated[datetime, Query(description="Fecha y hora de inicio (Ej: 2026-06-10T14:00:00)")],
    end_datetime: Annotated[datetime, Query(description="Fecha y hora de fin (Ej: 2026-06-10T23:59:59)")],
    db: Annotated[Session, Depends(get_db)]
):
    """Retorna películas únicas que tienen al menos una función dentro del rango de fecha y hora especificado."""
    peliculas = (
        db.query(Pelicula)
        .join(Funcion, Pelicula.id_pelicula == Funcion.id_pelicula)
        .filter(
            Funcion.fecha_hora >= start_datetime,
            Funcion.fecha_hora <= end_datetime,
            Pelicula.eliminado == False
        )
        .distinct()
        .all()
    )
    return peliculas