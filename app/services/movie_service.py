from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.movie import Pelicula
from app.models.genre import Genero
from app.models.review import Resena
from app.models.movie_genre import PeliculaGenero
from app.models.interaccion_pelicula import InteraccionPelicula
from fastapi import HTTPException


def get_movie_details(db: Session, movie_id: int, viewer_id: Optional[int] = None):
    movie = db.query(Pelicula).filter(Pelicula.id_pelicula == movie_id, Pelicula.eliminado == False).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    generos = (
        db.query(Genero.nombre_genero)
        .join(PeliculaGenero, PeliculaGenero.id_genero == Genero.id_genero)
        .filter(PeliculaGenero.id_pelicula == movie_id)
        .all()
    )

    stats = (
        db.query(
            func.avg(Resena.puntuacion_estrellas),
            func.count(Resena.id_resena),
        )
        .filter(Resena.id_pelicula == movie_id)
        .first()
    )

    promedio = float(stats[0]) if stats[0] else 0.0
    total = stats[1] if stats[1] else 0

    mi_calificacion = None
    es_favorita = False
    vista_por_mi = False
    if viewer_id is not None:
        mi_resena = (
            db.query(Resena.puntuacion_estrellas)
            .filter(Resena.id_pelicula == movie_id, Resena.id_usuario == viewer_id)
            .first()
        )
        mi_calificacion = mi_resena[0] if mi_resena else None

        mi_interaccion = (
            db.query(InteraccionPelicula)
            .filter(InteraccionPelicula.id_pelicula == movie_id, InteraccionPelicula.id_usuario == viewer_id)
            .first()
        )
        if mi_interaccion:
            es_favorita = mi_interaccion.favorita
            vista_por_mi = mi_interaccion.vista

    return {
        "id_pelicula": movie.id_pelicula,
        "titulo": movie.titulo,
        "sinopsis": movie.sinopsis,
        "duracion_minutos": movie.duracion_minutos,
        "clasificacion": movie.clasificacion,
        "anio_lanzamiento": movie.anio_lanzamiento,
        "url_poster": movie.url_poster,
        "url_banner": movie.url_banner,
        "url_trailer": movie.url_trailer,
        "estado_pelicula": movie.estado_pelicula,
        "elenco": movie.elenco,
        "director": movie.director,
        "generos": [g[0] for g in generos],
        "promedio_resenas": round(promedio, 1),
        "total_resenas": total,
        "total_vistas_comunidad": movie.total_vistas_comunidad,
        "total_favoritos_comunidad": movie.total_favoritos_comunidad,
        "mi_calificacion": mi_calificacion,
        "es_favorita": es_favorita,
        "vista_por_mi": vista_por_mi,
    }
