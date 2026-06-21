import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import interaccion_repository
from app.schemas.interaccion_pelicula import InteraccionPeliculaCreate, InteraccionPeliculaResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interacciones", tags=["interacciones"])


@router.post("/", response_model=InteraccionPeliculaResponse)
def upsert_interaccion(payload: InteraccionPeliculaCreate, db: Annotated[Session, Depends(get_db)]):
    data = payload.model_dump(exclude={"id_usuario", "id_pelicula"})
    return interaccion_repository.upsert_interaccion(db, payload.id_usuario, payload.id_pelicula, data)


@router.get("/usuario/{user_id}")
def list_interacciones(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return interaccion_repository.list_interacciones_by_user(db, user_id)
