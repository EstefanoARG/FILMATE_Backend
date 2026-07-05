import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db
from app.models.review import Resena
from app.models.movie import Pelicula
from app.repositories import review_repository
from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewWithUserResponse,
    ReviewWithMovieResponse,
    ReviewFeedItem,
    ToggleLikeRequest,
    ReviewLikeResponse,
    ReviewDetailResponse,
    ReviewCommentCreate,
    ReviewCommentResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/reviews", tags=["client reviews"])

@router.get("/user/{user_id}", response_model=List[ReviewWithMovieResponse])
def list_user_reviews(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return review_repository.list_reviews_by_user(db, user_id)


@router.get("/following/{user_id}", response_model=List[ReviewFeedItem])
def list_following_reviews(user_id: int, db: Annotated[Session, Depends(get_db)]):
    """Reseñas de las cuentas que el usuario sigue (HU-SOC-11)."""
    return review_repository.list_reviews_by_following(db, user_id)


@router.post("/", response_model=ReviewResponse, status_code=201)
def create_review(payload: ReviewCreate, db: Annotated[Session, Depends(get_db)]):
    review = Resena(
        id_usuario=payload.id_usuario,
        id_pelicula=payload.id_pelicula,
        puntuacion_estrellas=payload.puntuacion_estrellas,
        comentario=payload.comentario,
    )
    return review_repository.create_review(db, review)

@router.get("/movie/{movie_id}", response_model=List[ReviewWithUserResponse])
def list_reviews_for_movie(movie_id: int, db: Annotated[Session, Depends(get_db)], viewer_id: Optional[int] = None):
    return review_repository.list_reviews_for_movie(db, movie_id, viewer_id)


@router.post("/{review_id}/toggle-like", response_model=ReviewLikeResponse, responses={404: {"description": "Review not found"}})
def toggle_review_like(review_id: int, payload: ToggleLikeRequest, db: Annotated[Session, Depends(get_db)]):
    result = review_repository.toggle_review_like(db, review_id, payload.id_usuario)
    if result is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return result

@router.get("/user/{user_id}/rating-distribution")
def get_rating_distribution(user_id: int, db: Annotated[Session, Depends(get_db)]):
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
def get_user_rated_movies(user_id: int, db: Annotated[Session, Depends(get_db)]):
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

@router.put("/{review_id}", response_model=ReviewResponse, responses={404: {"description": "Review not found"}})
def update_review(review_id: int, payload: ReviewUpdate, db: Annotated[Session, Depends(get_db)]):
    updated = review_repository.update_review(db, review_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated


@router.delete("/{review_id}", responses={404: {"description": "Review not found"}})
def delete_review(review_id: int, db: Annotated[Session, Depends(get_db)]):
    deleted = review_repository.delete_review(db, review_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}


@router.get("/{review_id}", response_model=ReviewDetailResponse, responses={404: {"description": "Review not found"}})
def get_review_detail(review_id: int, db: Annotated[Session, Depends(get_db)], viewer_id: Optional[int] = None):
    """Detalle de una sola reseña (para la página de 'ver reseña original' con sus comentarios)."""
    detail = review_repository.get_review_detail(db, review_id, viewer_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Review not found")
    return detail


@router.post("/{review_id}/comments", response_model=ReviewCommentResponse, status_code=201, responses={404: {"description": "Review not found"}})
def add_comment(review_id: int, payload: ReviewCommentCreate, db: Annotated[Session, Depends(get_db)]):
    comment = review_repository.add_comment(db, review_id, payload.id_usuario, payload.texto)
    if not comment:
        raise HTTPException(status_code=404, detail="Review not found")
    return comment


@router.get("/{review_id}/comments", response_model=List[ReviewCommentResponse])
def list_comments(review_id: int, db: Annotated[Session, Depends(get_db)]):
    return review_repository.list_comments(db, review_id)


@router.delete("/{review_id}/comments/{comment_id}", responses={404: {"description": "Comment not found"}})
def delete_comment(review_id: int, comment_id: int, user_id: int, db: Annotated[Session, Depends(get_db)]):
    deleted = review_repository.delete_comment(db, comment_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comentario eliminado"}