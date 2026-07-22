from sqlalchemy.orm import Session
from app.models.seguidor import Seguidor
from app.models.historial_actividad import HistorialActividad
from app.models.user import Usuario
from typing import List


def follow(db: Session, id_seguidor: int, id_seguido: int) -> Seguidor:
    if id_seguidor == id_seguido:
        existing = (
            db.query(Seguidor)
            .filter(Seguidor.id_seguidor == id_seguidor, Seguidor.id_seguido == id_seguido)
            .first()
        )
        return existing

    existing = (
        db.query(Seguidor)
        .filter(Seguidor.id_seguidor == id_seguidor, Seguidor.id_seguido == id_seguido)
        .first()
    )
    if existing:
        return existing
    s = Seguidor(id_seguidor=id_seguidor, id_seguido=id_seguido)
    db.add(s)
    # El trigger de BD ya registra el evento en el feed de quien sigue (SEGUIDOR);
    # esta fila avisa al usuario seguido, que de otra forma no se enteraría.
    db.add(
        HistorialActividad(
            id_usuario=id_seguido,
            tipo_evento="SEGUIDOR_RECIBIDO",
            id_referencia_usuario=id_seguidor,
            texto_breve="Tienes un nuevo seguidor.",
        )
    )
    db.commit()
    return s


def unfollow(db: Session, id_seguidor: int, id_seguido: int) -> bool:
    s = (
        db.query(Seguidor)
        .filter(Seguidor.id_seguidor == id_seguidor, Seguidor.id_seguido == id_seguido)
        .first()
    )
    if not s:
        return False
    db.delete(s)
    db.commit()
    return True


def list_followers(db: Session, user_id: int) -> List[Seguidor]:
    return db.query(Seguidor).filter(Seguidor.id_seguido == user_id).all()


def list_following(db: Session, user_id: int) -> List[Seguidor]:
    rows = (
        db.query(Seguidor, Usuario)
        .join(Usuario, Usuario.id_usuario == Seguidor.id_seguido)
        .filter(Seguidor.id_seguidor == user_id)
        .all()
    )

    return [
        {
            "id_seguidor": seguimiento.id_seguidor,
            "id_seguido": seguimiento.id_seguido,
            "fecha_seguimiento": seguimiento.fecha_seguimiento,
            "seguido": {
                "id_usuario": seguido.id_usuario,
                "username": seguido.username,
                "nombre": seguido.nombre,
                "correo": seguido.correo,
                "url_perfil": seguido.url_perfil,
            },
        }
        for seguimiento, seguido in rows
    ]


def is_following(db: Session, id_seguidor: int, id_seguido: int) -> bool:
    return (
        db.query(Seguidor)
        .filter(Seguidor.id_seguidor == id_seguidor, Seguidor.id_seguido == id_seguido)
        .first()
        is not None
    )


def count_followers(db: Session, user_id: int) -> int:
    return db.query(Seguidor).filter(Seguidor.id_seguido == user_id).count()


def count_following(db: Session, user_id: int) -> int:
    return db.query(Seguidor).filter(Seguidor.id_seguidor == user_id).count()
