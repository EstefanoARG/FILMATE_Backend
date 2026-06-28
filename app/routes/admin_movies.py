from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Annotated, List
import logging

from app.core.dependencies import get_db
from app.models.genre import Genero
from app.models.movie import Pelicula
from app.schemas.movie import (
    MovieCreate, MovieResponse, MovieUpdate,
    TMDBMovieCreate, TMDBPreviewResponse, TMDBSearchItem,
)
from app.repositories import movie_repository
from app.services.tmdb_service import search_movie, get_movie_preview, map_tmdb_genres_to_local

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/movies", tags=["admin movies"])


@router.get("/", response_model=List[MovieResponse])
def admin_list_movies(db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 200):
    return movie_repository.list_movies(db, skip=skip, limit=limit)


@router.post("/", response_model=MovieResponse, responses={500: {"description": "Internal server error"}})
def create_movie(payload: MovieCreate, db: Annotated[Session, Depends(get_db)]):
    try:
        from app.models.movie_genre import PeliculaGenero

        if payload.tmdb_id:
            existing = db.query(Pelicula).filter(Pelicula.id_tmdb == payload.tmdb_id).first()
            if existing:
                raise HTTPException(status_code=409, detail="Esta película ya existe en el catálogo")

        movie = Pelicula(
            id_tmdb=payload.tmdb_id,
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
    except HTTPException:
        raise
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


@router.get("/tmdb/search", response_model=List[TMDBSearchItem])
def tmdb_search(query: Annotated[str, Query(min_length=2)]):
    try:
        return search_movie(query)
    except Exception as e:
        logger.exception("Error searching TMDB")
        raise HTTPException(status_code=502, detail="Error al consultar TMDb")


@router.get("/tmdb/{tmdb_id}/preview", response_model=TMDBPreviewResponse)
def tmdb_preview(tmdb_id: int):
    try:
        return get_movie_preview(tmdb_id)
    except Exception as e:
        logger.exception("Error fetching TMDB preview")
        raise HTTPException(status_code=502, detail="Error al obtener vista previa de TMDb")


@router.post("/tmdb/{tmdb_id}", response_model=MovieResponse, responses={409: {"description": "Duplicate movie"}})
def create_movie_from_tmdb(
    tmdb_id: int,
    payload: TMDBMovieCreate,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        from app.models.movie_genre import PeliculaGenero

        existing = db.query(Pelicula).filter(Pelicula.id_tmdb == tmdb_id).first()
        if existing:
            raise HTTPException(status_code=409, detail="Esta película ya existe en el catálogo")

        preview = get_movie_preview(tmdb_id)

        clasificacion = payload.clasificacion or preview.get("clasificacion", "PG-13")
        url_trailer = payload.url_trailer or preview.get("url_trailer")

        movie = Pelicula(
            id_tmdb=tmdb_id,
            titulo=preview["titulo"],
            anio_lanzamiento=preview["anio_lanzamiento"],
            duracion_minutos=preview["duracion_minutos"],
            clasificacion=clasificacion,
            estado_pelicula=payload.estado_pelicula,
            url_poster=preview["url_poster"],
            url_banner=preview.get("url_banner"),
            url_trailer=url_trailer,
            sinopsis=preview.get("sinopsis"),
            elenco=preview.get("elenco"),
            director=preview["director"],
        )
        db.add(movie)
        db.commit()
        db.refresh(movie)

        genres = db.query(Genero).all()
        genre_ids = map_tmdb_genres_to_local(preview.get("tmdb_genres", []), genres)
        for gid in genre_ids:
            db.add(PeliculaGenero(id_pelicula=movie.id_pelicula, id_genero=gid))
        db.commit()

        return movie
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.exception("Error creating movie from TMDB")
        raise HTTPException(status_code=500, detail=str(e))
