from sqlalchemy.orm import Session
from app.models.room import Sala


def list_rooms(db: Session):
    return db.query(Sala).filter(Sala.eliminado == False).all()


def get_room(db: Session, room_id: int):
    return db.query(Sala).filter(Sala.id_sala == room_id, Sala.eliminado == False).first()


def create_room(db: Session, room: Sala):
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update_room(db: Session, room: Sala):
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: Sala):
    db.delete(room)
    db.commit()
