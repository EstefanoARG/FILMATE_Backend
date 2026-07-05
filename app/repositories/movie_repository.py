from sqlalchemy.orm import Session, joinedload
from app.models.movie import Pelicula
from app.models.movie_genre import PeliculaGenero
from typing import List, Optional


def get_movie(db: Session, movie_id: int) -> Optional[Pelicula]:
    return db.query(Pelicula).filter(Pelicula.id_pelicula == movie_id, Pelicula.eliminado == False).first()


ORDER_OPTIONS = {
    "titulo_asc": Pelicula.titulo.asc(),
    "titulo_desc": Pelicula.titulo.desc(),
    "anio_asc": Pelicula.anio_lanzamiento.asc(),
    "anio_desc": Pelicula.anio_lanzamiento.desc(),
    "recientes": Pelicula.id_pelicula.desc(),
}


def list_movies(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    genero_id: Optional[int] = None,
    clasificacion: Optional[str] = None,
    anio_lanzamiento: Optional[int] = None,
    estado_pelicula: Optional[str] = None,
    order_by: Optional[str] = None,
) -> List[Pelicula]:
    query = db.query(Pelicula).options(joinedload(Pelicula.generos)).filter(Pelicula.eliminado == False)
    if genero_id is not None:
        query = query.filter(Pelicula.generos.any(id_genero=genero_id))
    if clasificacion is not None:
        query = query.filter(Pelicula.clasificacion == clasificacion)
    if anio_lanzamiento is not None:
        query = query.filter(Pelicula.anio_lanzamiento == anio_lanzamiento)
    if estado_pelicula is not None:
        query = query.filter(Pelicula.estado_pelicula == estado_pelicula)

    query = query.order_by(ORDER_OPTIONS.get(order_by, Pelicula.id_pelicula.desc()))
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
