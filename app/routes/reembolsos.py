import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import reembolso_repository
from app.schemas.solicitud_reembolso import SolicitudReembolsoCreate, SolicitudReembolsoResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reembolsos", tags=["reembolsos"])


@router.post("/", response_model=SolicitudReembolsoResponse, status_code=201)
def create_solicitud(payload: SolicitudReembolsoCreate, db: Session = Depends(get_db)):
    return reembolso_repository.create_solicitud(
        db,
        id_transaccion=payload.id_transaccion,
        motivo=payload.motivo,
        monto_reembolsado=payload.monto_reembolsado,
        tipo_reembolso=payload.tipo_reembolso,
    )


@router.get("/mis-solicitudes", response_model=List[SolicitudReembolsoResponse])
def list_mis_solicitudes(id_usuario: int = Query(...), db: Session = Depends(get_db)):
    return reembolso_repository.list_solicitudes_by_user(db, id_usuario)
