import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.cinema import Cine
from app.schemas.cinema import CinemaCreate, CinemaResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/cinemas", tags=["admin cinemas"])


@router.get("/", response_model=List[CinemaResponse])
def admin_list_cinemas(db: Session = Depends(get_db)):
    return db.query(Cine).filter(Cine.eliminado == False).all()


@router.post("/", response_model=CinemaResponse, status_code=201)
def create_cinema(payload: CinemaCreate, db: Session = Depends(get_db)):
    cine = Cine(**payload.model_dump())
    db.add(cine)
    db.commit()
    db.refresh(cine)
    return cine


@router.put("/{cinema_id}", response_model=CinemaResponse)
def update_cinema(cinema_id: int, payload: CinemaCreate, db: Session = Depends(get_db)):
    cine = db.query(Cine).filter(Cine.id_cine == cinema_id, Cine.eliminado == False).first()
    if not cine:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    for key, value in payload.model_dump().items():
        setattr(cine, key, value)
    db.commit()
    db.refresh(cine)
    return cine


@router.delete("/{cinema_id}")
def delete_cinema(cinema_id: int, db: Session = Depends(get_db)):
    from datetime import datetime
    cine = db.query(Cine).filter(Cine.id_cine == cinema_id, Cine.eliminado == False).first()
    if not cine:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    cine.eliminado = True
    cine.fecha_eliminacion = datetime.now()
    db.commit()
    return {"message": "Cine desactivado"}
