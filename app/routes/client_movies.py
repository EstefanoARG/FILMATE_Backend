import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import movie_repository
from app.schemas.movie import MovieResponse, MovieDetailsResponse
from app.services.movie_service import get_movie_details

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