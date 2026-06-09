from sqlalchemy.orm import Session
from app.models.seguidor import Seguidor
from typing import List


def follow(db: Session, id_seguidor: int, id_seguido: int) -> Seguidor:
    existing = (
        db.query(Seguidor)
        .filter(Seguidor.id_seguidor == id_seguidor, Seguidor.id_seguido == id_seguido)
        .first()
    )
    if existing:
        return existing
    s = Seguidor(id_seguidor=id_seguidor, id_seguido=id_seguido)
    db.add(s)
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
    return db.query(Seguidor).filter(Seguidor.id_seguidor == user_id).all()
