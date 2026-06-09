from sqlalchemy.orm import Session
from app.models.coleccion import Coleccion
from app.models.coleccion_pelicula import ColeccionPelicula
from typing import Optional


def list_colecciones(db: Session, user_id: int):
    return db.query(Coleccion).filter(Coleccion.id_usuario == user_id, Coleccion.eliminado == False).all()


def get_coleccion(db: Session, coleccion_id: int) -> Optional[Coleccion]:
    return db.query(Coleccion).filter(Coleccion.id_coleccion == coleccion_id, Coleccion.eliminado == False).first()


def create_coleccion(db: Session, coleccion: Coleccion) -> Coleccion:
    db.add(coleccion)
    db.commit()
    db.refresh(coleccion)
    return coleccion


def add_pelicula_to_coleccion(db: Session, coleccion_id: int, pelicula_id: int) -> ColeccionPelicula:
    cp = ColeccionPelicula(id_coleccion=coleccion_id, id_pelicula=pelicula_id)
    db.add(cp)
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
