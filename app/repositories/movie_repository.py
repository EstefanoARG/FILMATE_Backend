from sqlalchemy.orm import Session, joinedload
from app.models.movie import Pelicula
from app.models.movie_genre import PeliculaGenero
from typing import List, Optional


def get_movie(db: Session, movie_id: int) -> Optional[Pelicula]:
    return db.query(Pelicula).filter(Pelicula.id_pelicula == movie_id, Pelicula.eliminado == False).first()


def list_movies(db: Session, skip: int = 0, limit: int = 100, genero_id: Optional[int] = None) -> List[Pelicula]:
    query = db.query(Pelicula).options(joinedload(Pelicula.generos)).filter(Pelicula.eliminado == False)
    if genero_id is not None:
        query = query.filter(Pelicula.generos.any(id_genero=genero_id))
    return query.offset(skip).limit(limit).all()


def create_movie(db: Session, movie: Pelicula) -> Pelicula:
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie


def update_movie(db: Session, movie_id: int, data: dict) -> Optional[Pelicula]:
    movie = get_movie(db, movie_id)
    if not movie:
        return None

    for key, value in data.items():
        if hasattr(movie, key) and value is not None:
            setattr(movie, key, value)

    if "generos" in data:
        db.query(PeliculaGenero).filter(PeliculaGenero.id_pelicula == movie_id).delete()
        for genero_id in data["generos"]:
            db.add(PeliculaGenero(id_pelicula=movie_id, id_genero=genero_id))

    db.commit()
    db.refresh(movie)
    return movie


def soft_delete_movie(db: Session, movie_id: int) -> Optional[Pelicula]:
    movie = db.query(Pelicula).filter(Pelicula.id_pelicula == movie_id).first()
    if not movie:
        return None
    movie.eliminado = True
    from datetime import datetime
    movie.fecha_eliminacion = datetime.now()
    db.commit()
    return movie
