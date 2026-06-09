import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.cinema import Cine
from app.schemas.cinema import CinemaResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cinemas", tags=["cinemas"])


@router.get("/", response_model=List[CinemaResponse])
def list_cinemas(db: Session = Depends(get_db)):
    return db.query(Cine).filter(Cine.eliminado == False).all()


@router.get("/{cinema_id}", response_model=CinemaResponse)
def get_cinema(cinema_id: int, db: Session = Depends(get_db)):
    cinema = db.query(Cine).filter(Cine.id_cine == cinema_id, Cine.eliminado == False).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    return cinema
