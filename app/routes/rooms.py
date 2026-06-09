import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.room import Sala
from app.repositories import room_repository
from app.schemas.room import RoomCreate, RoomResponse, RoomUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/rooms", tags=["admin rooms"])


@router.get("/", response_model=List[RoomResponse])
def list_rooms(db: Session = Depends(get_db)):
    return room_repository.list_rooms(db)


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = room_repository.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return room


@router.post("/", response_model=RoomResponse, status_code=201)
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    room = Sala(**payload.model_dump())
    return room_repository.create_room(db, room)


@router.put("/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, payload: RoomUpdate, db: Session = Depends(get_db)):
    room = room_repository.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, key, value)
    return room_repository.update_room(db, room)


@router.delete("/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = room_repository.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    room.eliminado = True
    from datetime import datetime
    room.fecha_eliminacion = datetime.now()
    db.commit()
    return {"message": "Sala eliminada"}
