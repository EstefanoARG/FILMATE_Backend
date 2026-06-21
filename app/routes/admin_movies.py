from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
import logging

from app.core.dependencies import get_db
from app.models.genre import Genero
from app.models.movie import Pelicula
from app.schemas.movie import MovieCreate, MovieResponse, MovieUpdate
from app.repositories import movie_repository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/movies", tags=["admin movies"])


@router.get("/", response_model=List[MovieResponse])
def admin_list_movies(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 200):
    return movie_repository.list_movies(db, skip=skip, limit=limit)


@router.post("/", response_model=MovieResponse, responses={500: {"description": "Internal server error"}})
def create_movie(payload: MovieCreate, db: Annotated[Session, Depends(get_db)]):
    try:
        from app.models.movie_genre import PeliculaGenero
        movie = Pelicula(
            titulo=payload.titulo,
            anio_lanzamiento=payload.anio_lanzamiento,
            duracion_minutos=payload.duracion_minutos,
            clasificacion=payload.clasificacion,
            estado_pelicula=payload.estado_pelicula,
            url_poster=payload.url_poster,
            url_banner=payload.url_banner,
            url_trailer=payload.url_trailer,
            sinopsis=payload.sinopsis,
            elenco=payload.elenco,
            director=payload.director,
        )
        db.add(movie)
        db.commit()
        db.refresh(movie)

        for genero_id in payload.generos:
            db.add(PeliculaGenero(id_pelicula=movie.id_pelicula, id_genero=genero_id))
        db.commit()
        return movie
    except Exception as e:
        db.rollback()
        logger.exception("Error en POST /admin/movies")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{movie_id}", response_model=MovieResponse, responses={404: {"description": "Movie not found"}})
def update_movie(movie_id: int, payload: MovieUpdate, db: Annotated[Session, Depends(get_db)]):
    data = payload.model_dump(exclude_unset=True)
    updated = movie_repository.update_movie(db, movie_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated


@router.delete("/{movie_id}", responses={404: {"description": "Movie not found"}})
def delete_movie(movie_id: int, db: Annotated[Session, Depends(get_db)]):
    result = movie_repository.soft_delete_movie(db, movie_id)
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deactivated successfully"}


@router.get("/meta/genres")
def list_genres(db: Annotated[Session, Depends(get_db)]):
    return db.query(Genero).order_by(Genero.nombre_genero.asc()).all()


@router.get("/meta/classifications")
def list_classifications(db: Annotated[Session, Depends(get_db)]):
    from sqlalchemy import distinct
    items = db.query(distinct(Pelicula.clasificacion)).filter(Pelicula.clasificacion.isnot(None)).all()
    return [item[0] for item in items]


@router.get("/meta/statuses")
def list_statuses(db: Annotated[Session, Depends(get_db)]):
    from sqlalchemy import distinct
    items = db.query(distinct(Pelicula.estado_pelicula)).all()
    return [item[0] for item in items]


@router.get("/meta/categories")
def list_categories(db: Annotated[Session, Depends(get_db)]):
    from sqlalchemy import distinct
    items = db.query(distinct(Pelicula.estado_pelicula)).all()
    return [item[0] for item in items]
