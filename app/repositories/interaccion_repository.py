from sqlalchemy.orm import Session
from app.models.interaccion_pelicula import InteraccionPelicula
from typing import Optional


def get_interaccion(db: Session, user_id: int, movie_id: int) -> Optional[InteraccionPelicula]:
    return (
        db.query(InteraccionPelicula)
        .filter(
            InteraccionPelicula.id_usuario == user_id,
            InteraccionPelicula.id_pelicula == movie_id,
        )
        .first()
    )


def upsert_interaccion(db: Session, user_id: int, movie_id: int, data: dict) -> InteraccionPelicula:
    interaccion = get_interaccion(db, user_id, movie_id)
    if not interaccion:
        interaccion = InteraccionPelicula(id_usuario=user_id, id_pelicula=movie_id)
        db.add(interaccion)
    for key, value in data.items():
        if hasattr(interaccion, key):
            setattr(interaccion, key, value)
    db.commit()
    db.refresh(interaccion)
    return interaccion


def list_interacciones_by_user(db: Session, user_id: int):
    return db.query(InteraccionPelicula).filter(InteraccionPelicula.id_usuario == user_id).all()
