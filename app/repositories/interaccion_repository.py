from sqlalchemy.orm import Session
from app.models.interaccion_pelicula import InteraccionPelicula
from app.models.historial_actividad import HistorialActividad
from app.models.movie import Pelicula
from typing import Optional


def _log_evento(db: Session, user_id: int, tipo: str, pelicula_id: int = None, texto: str = None):
    evento = HistorialActividad(
        id_usuario=user_id,
        tipo_evento=tipo,
        id_referencia_pelicula=pelicula_id,
        texto_breve=texto,
    )
    db.add(evento)


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
    existia = True
    interaccion = get_interaccion(db, user_id, movie_id)
    if not interaccion:
        existia = False
        interaccion = InteraccionPelicula(id_usuario=user_id, id_pelicula=movie_id)
        db.add(interaccion)
        db.flush()

    old_vista = interaccion.vista
    old_favorita = interaccion.favorita

    for key, value in data.items():
        if hasattr(interaccion, key):
            setattr(interaccion, key, value)

    pelicula = db.get(Pelicula, movie_id)

    if not existia and data.get("favorita"):
        _log_evento(db, user_id, "FAVORITO", movie_id, f"Agregó {pelicula.titulo if pelicula else ''} a favoritos")
    elif existia and data.get("favorita") and not old_favorita:
        _log_evento(db, user_id, "FAVORITO", movie_id, f"Agregó {pelicula.titulo if pelicula else ''} a favoritos")

    if data.get("vista") and not old_vista:
        _log_evento(db, user_id, "VISTA", movie_id, f"Vio {pelicula.titulo if pelicula else ''}")

    db.commit()
    db.refresh(interaccion)
    return interaccion


def list_interacciones_by_user(db: Session, user_id: int):
    return db.query(InteraccionPelicula).filter(InteraccionPelicula.id_usuario == user_id).all()


def delete_interaccion(db: Session, user_id: int, movie_id: int) -> bool:
    interaccion = get_interaccion(db, user_id, movie_id)
    if not interaccion:
        return False
    db.delete(interaccion)
    db.commit()
    return True
