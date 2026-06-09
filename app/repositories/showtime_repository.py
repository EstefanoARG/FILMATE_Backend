from sqlalchemy.orm import Session
from app.models.showtime import Funcion


def create_showtime(db: Session, showtime: Funcion):
    db.add(showtime)
    db.commit()
    db.refresh(showtime)
    return showtime


def list_showtimes(db: Session):
    return db.query(Funcion).all()


def get_showtime(db: Session, showtime_id: int):
    return db.query(Funcion).filter(Funcion.id_funcion == showtime_id).first()


def update_showtime(db: Session, showtime_id: int, data: dict):
    showtime = get_showtime(db, showtime_id)
    if not showtime:
        return None
    for key, value in data.items():
        setattr(showtime, key, value)
    db.commit()
    db.refresh(showtime)
    return showtime


def delete_showtime(db: Session, showtime_id: int):
    showtime = get_showtime(db, showtime_id)
    if not showtime:
        return None
    db.delete(showtime)
    db.commit()
    return showtime
