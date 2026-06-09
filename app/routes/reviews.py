import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.review import Resena
from app.repositories import review_repository
from app.schemas.review import ReviewCreate, ReviewResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse, status_code=201)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    review = Resena(
        id_usuario=payload.id_usuario,
        id_pelicula=payload.id_pelicula,
        puntuacion_estrellas=payload.puntuacion_estrellas,
        comentario=payload.comentario,
    )
    return review_repository.create_review(db, review)


@router.get("/movie/{movie_id}", response_model=List[ReviewResponse])
def list_reviews_for_movie(movie_id: int, db: Session = Depends(get_db)):
    return review_repository.list_reviews_for_movie(db, movie_id)


@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    deleted = review_repository.delete_review(db, review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}
