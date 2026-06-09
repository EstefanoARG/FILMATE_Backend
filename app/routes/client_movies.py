import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import movie_repository
from app.schemas.movie import MovieResponse, MovieDetailsResponse
from app.services.movie_service import get_movie_details
from app.models.movie import Pelicula
from app.models.interaccion_pelicula import InteraccionPelicula
from datetime import datetime
from app.models.movie import Pelicula
from app.models.showtime import Funcion
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/movies", tags=["client movies"])

@router.get("/", response_model=List[MovieResponse])
def list_movies(skip: int = 0, limit: int = 50, genero_id: Optional[int] = None, db: Session = Depends(get_db)):
    return movie_repository.list_movies(db, skip=skip, limit=limit, genero_id=genero_id)

@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = movie_repository.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@router.get("/{movie_id}/details", response_model=MovieDetailsResponse)
def movie_details(movie_id: int, db: Session = Depends(get_db)):
    return get_movie_details(db, movie_id)

@router.get("/favorites/{user_id}", response_model=List[MovieResponse])
def get_favorite_movies(user_id: int, db: Session = Depends(get_db)):
    """
    Retorna la lista de películas marcadas como favoritas por un usuario específico.
    """
    favoritas = (
        db.query(Pelicula)
        .join(InteraccionPelicula, Pelicula.id_pelicula == InteraccionPelicula.id_pelicula)
        .filter(
            InteraccionPelicula.id_usuario == user_id,
            InteraccionPelicula.favorita == True,
            Pelicula.eliminado == False
        )
        .order_by(InteraccionPelicula.fecha_favorito.desc()) # Opcional: ordenar por las agregadas más recientemente
        .all()
    )
    return favoritas

@router.get("/available/by-datetime", response_model=List[MovieResponse])
def get_movies_by_datetime_range(
    start_datetime: datetime = Query(..., description="Fecha y hora de inicio (Ej: 2026-06-10T14:00:00)"),
    end_datetime: datetime = Query(..., description="Fecha y hora de fin (Ej: 2026-06-10T23:59:59)"),
    db: Session = Depends(get_db)
):
    """
    Retorna películas únicas que tienen al menos una función dentro del rango de fecha y hora especificado.
    """
    peliculas = (
        db.query(Pelicula)
        .join(Funcion, Pelicula.id_pelicula == Funcion.id_pelicula)
        .filter(
            Funcion.fecha_hora >= start_datetime,
            Funcion.fecha_hora <= end_datetime,
            Pelicula.eliminado == False
        )
        .distinct() # evita devolver la misma película 5 veces si tiene 5 funciones en ese rango
        .all()
    )
    return peliculas