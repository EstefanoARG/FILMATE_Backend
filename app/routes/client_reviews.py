import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db
from app.models.review import Resena
from app.models.movie import Pelicula
from app.repositories import review_repository
from app.schemas.review import ReviewCreate, ReviewResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/reviews", tags=["client reviews"])

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

@router.get("/user/{user_id}/rating-distribution")
def get_rating_distribution(user_id: int, db: Session = Depends(get_db)):
    """Para llenar 'Clasificación Personal' con datos reales (1 a 5 estrellas)."""
    distribucion = (
        db.query(
            Resena.puntuacion_estrellas,
            func.count(Resena.id_resena).label('total')
        )
        .filter(Resena.id_usuario == user_id)
        .group_by(Resena.puntuacion_estrellas)
        .all()
    )
    
    # Inicializa el diccionario {"1": 0, "2": 0... "5": 0}
    resultado = {str(i): 0 for i in range(1, 6)}
    for estrellas, total in distribucion:
        if estrellas is not None:
            resultado[str(estrellas)] = total
            
    return resultado

@router.get("/user/{user_id}/movies")
def get_user_rated_movies(user_id: int, db: Session = Depends(get_db)):
    """Lista de todas las películas calificadas y qué calificación se le dio."""
    resultados = (
        db.query(Resena.puntuacion_estrellas, Pelicula)
        .join(Pelicula, Resena.id_pelicula == Pelicula.id_pelicula)
        .filter(Resena.id_usuario == user_id, Pelicula.eliminado == False)
        .order_by(Resena.fecha_publicacion.desc())
        .all()
    )
    
    return [
        {
            "calificacion": calificacion,
            # FastAPI convertirá automáticamente el diccionario a JSON
            "pelicula": {
                "id_pelicula": pelicula.id_pelicula,
                "titulo": pelicula.titulo,
                "url_poster": pelicula.url_poster,
                "anio_lanzamiento": pelicula.anio_lanzamiento
            }
        }
        for calificacion, pelicula in resultados
    ]

@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    deleted = review_repository.delete_review(db, review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}