import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.cinema import Cine
from app.schemas.cinema import CinemaResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cinemas", tags=["cinemas"])


@router.get("/", response_model=List[CinemaResponse])
def list_cinemas(db: Annotated[Session, Depends(get_db)]):
    return db.query(Cine).filter(Cine.eliminado == False).all()


@router.get("/{cinema_id}", response_model=CinemaResponse, responses={404: {"description": "Cine no encontrado"}})
def get_cinema(cinema_id: int, db: Annotated[Session, Depends(get_db)]):
    cinema = db.query(Cine).filter(Cine.id_cine == cinema_id, Cine.eliminado == False).first()
    if not cinema:
        raise HTTPException(status_code=404, detail="Cine no encontrado")
    return cinema
