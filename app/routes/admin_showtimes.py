import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.showtime import Funcion
from app.repositories import showtime_repository
from app.schemas.showtime import ShowtimeCreate, ShowtimeResponse, ShowtimeUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/showtimes", tags=["admin showtimes"])


@router.get("/", response_model=List[ShowtimeResponse])
def admin_list_showtimes(db: Session = Depends(get_db)):
    return showtime_repository.list_showtimes(db)


@router.post("/", response_model=ShowtimeResponse, status_code=201)
def create_showtime(payload: ShowtimeCreate, db: Session = Depends(get_db)):
    logger.info("POST /admin/showtimes/ - pelicula=%s sala=%s", payload.id_pelicula, payload.id_sala)
    funcion = Funcion(
        id_pelicula=payload.id_pelicula,
        id_sala=payload.id_sala,
        fecha_hora=payload.fecha_hora,
        precio_base=payload.precio_base,
    )
    return showtime_repository.create_showtime(db, funcion)


@router.put("/{showtime_id}", response_model=ShowtimeResponse)
def update_showtime(showtime_id: int, payload: ShowtimeUpdate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    updated = showtime_repository.update_showtime(db, showtime_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Función no encontrada")
    return updated


@router.delete("/{showtime_id}")
def delete_showtime(showtime_id: int, db: Session = Depends(get_db)):
    deleted = showtime_repository.delete_showtime(db, showtime_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Función no encontrada")
    return {"message": "Función eliminada"}
