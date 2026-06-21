import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import reembolso_repository
from app.schemas.solicitud_reembolso import SolicitudReembolsoCreate, SolicitudReembolsoResponse, SolicitudReembolsoUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/reembolsos", tags=["admin reembolsos"])


@router.get("/", response_model=List[SolicitudReembolsoResponse])
def list_solicitudes(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    estado: Optional[str] = None,
):
    return reembolso_repository.list_solicitudes_admin(db, estado=estado, skip=skip, limit=limit)


@router.get("/metricas")
def get_metricas(db: Annotated[Session, Depends(get_db)]):
    return reembolso_repository.count_solicitudes_by_estado(db)


@router.get("/{solicitud_id}", response_model=SolicitudReembolsoResponse, responses={404: {"description": "Solicitud no encontrada"}})
def get_solicitud(solicitud_id: int, db: Annotated[Session, Depends(get_db)]):
    solicitud = reembolso_repository.get_solicitud(db, solicitud_id)
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return solicitud


@router.put("/{solicitud_id}", response_model=SolicitudReembolsoResponse, responses={404: {"description": "Solicitud no encontrada"}})
def resolve_solicitud(solicitud_id: int, payload: SolicitudReembolsoUpdate, db: Annotated[Session, Depends(get_db)]):
    solicitud = reembolso_repository.resolve_solicitud(
        db,
        solicitud_id,
        estado_solicitud=payload.estado_solicitud,
        comentario_administrador=payload.comentario_administrador,
    )
    if not solicitud:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return solicitud
