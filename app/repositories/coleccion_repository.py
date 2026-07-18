from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from app.models.coleccion import Coleccion
from app.models.coleccion_pelicula import ColeccionPelicula
from app.models.historial_actividad import HistorialActividad
from app.models.movie import Pelicula
from typing import Optional


def list_colecciones(db: Session, user_id: int):
    return db.query(Coleccion).filter(Coleccion.id_usuario == user_id, Coleccion.eliminado == False).all()


def list_colecciones_with_movies(db: Session, user_id: int):
    colecciones = list_colecciones(db, user_id)
    result = []

    for coleccion in colecciones:
        peliculas = get_peliculas_from_coleccion(db, coleccion.id_coleccion)
        result.append((coleccion, peliculas))

    return result


def get_coleccion(db: Session, coleccion_id: int) -> Optional[Coleccion]:
    return db.query(Coleccion).filter(Coleccion.id_coleccion == coleccion_id, Coleccion.eliminado == False).first()


def get_coleccion_detail(db: Session, coleccion_id: int):
    coleccion = get_coleccion(db, coleccion_id)
    if not coleccion:
        return None
    peliculas = (
        db.query(Pelicula)
        .join(ColeccionPelicula, Pelicula.id_pelicula == ColeccionPelicula.id_pelicula)
        .filter(ColeccionPelicula.id_coleccion == coleccion_id)
        .all()
    )
    return coleccion, peliculas


def get_peliculas_from_coleccion(db: Session, coleccion_id: int):
    return (
        db.query(Pelicula)
        .join(ColeccionPelicula, Pelicula.id_pelicula == ColeccionPelicula.id_pelicula)
        .filter(ColeccionPelicula.id_coleccion == coleccion_id)
        .all()
    )


def create_coleccion(db: Session, coleccion: Coleccion) -> Coleccion:
    db.add(coleccion)
    db.commit()
    db.refresh(coleccion)
    evento = HistorialActividad(
        id_usuario=coleccion.id_usuario,
        tipo_evento="COLECCION",
        id_referencia_pelicula=None,
        texto_breve=f"Creó la lista '{coleccion.titulo_coleccion}'",
    )
    db.add(evento)
    db.commit()
    return coleccion


def update_coleccion(db: Session, coleccion_id: int, data: dict):
    coleccion = get_coleccion(db, coleccion_id)
    if not coleccion:
        return None
    for key, value in data.items():
        if hasattr(coleccion, key) and value is not None:
            setattr(coleccion, key, value)
    db.commit()
    db.refresh(coleccion)
    return coleccion


def soft_delete_coleccion(db: Session, coleccion_id: int) -> bool:
    coleccion = get_coleccion(db, coleccion_id)
    if not coleccion:
        return False
    coleccion.eliminado = True
    coleccion.fecha_eliminacion = datetime.now()
    db.commit()
    return True


def add_pelicula_to_coleccion(db: Session, coleccion_id: int, pelicula_id: int) -> ColeccionPelicula:
    cp = ColeccionPelicula(id_coleccion=coleccion_id, id_pelicula=pelicula_id)
    db.add(cp)
    db.commit()
    coleccion = get_coleccion(db, coleccion_id)
    pelicula = db.get(Pelicula, pelicula_id)
    if coleccion:
        evento = HistorialActividad(
            id_usuario=coleccion.id_usuario,
            tipo_evento="COLECCION",
            id_referencia_pelicula=pelicula_id,
            texto_breve=f"Agregó '{pelicula.titulo if pelicula else ''}' a la lista '{coleccion.titulo_coleccion}'",
        )
        db.add(evento)
        db.commit()
    return cp


def remove_pelicula_from_coleccion(db: Session, coleccion_id: int, pelicula_id: int) -> bool:
    cp = (
        db.query(ColeccionPelicula)
        .filter(
            ColeccionPelicula.id_coleccion == coleccion_id,
            ColeccionPelicula.id_pelicula == pelicula_id,
        )
        .first()
    )
    if not cp:
        return False
    db.delete(cp)
    db.commit()
    return True
