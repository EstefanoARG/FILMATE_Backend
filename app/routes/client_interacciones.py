import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import interaccion_repository
from app.schemas.interaccion_pelicula import InteraccionPeliculaCreate, InteraccionPeliculaResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/interacciones", tags=["client interacciones"])

@router.post("/", response_model=InteraccionPeliculaResponse)
def upsert_interaccion(payload: InteraccionPeliculaCreate, db: Annotated[Session, Depends(get_db)]):
    data = payload.model_dump(exclude={"id_usuario", "id_pelicula"})
    return interaccion_repository.upsert_interaccion(db, payload.id_usuario, payload.id_pelicula, data)

@router.get("/usuario/{user_id}/pelicula/{movie_id}", response_model=InteraccionPeliculaResponse, responses={404: {"description": "Interacción no encontrada"}})
def get_interaccion(user_id: int, movie_id: int, db: Annotated[Session, Depends(get_db)]):
    interaccion = interaccion_repository.get_interaccion(db, user_id, movie_id)
    if not interaccion:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return interaccion


@router.get("/usuario/{user_id}")
def list_interacciones(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return interaccion_repository.list_interacciones_by_user(db, user_id)

@router.delete("/usuario/{user_id}/pelicula/{movie_id}", responses={404: {"description": "Interacción no encontrada"}})
def delete_interaccion(user_id: int, movie_id: int, db: Annotated[Session, Depends(get_db)]):
    deleted = interaccion_repository.delete_interaccion(db, user_id, movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Interacción no encontrada")
    return {"message": "Interacción eliminada"}


@router.post("/usuario/{user_id}/pelicula/{movie_id}/toggle-vista", response_model=InteraccionPeliculaResponse)
def toggle_vista(user_id: int, movie_id: int, db: Annotated[Session, Depends(get_db)]):
    """Alterna visto/no visto en un solo click, sin riesgo de contar de más por dobles clicks."""
    return interaccion_repository.toggle_vista(db, user_id, movie_id)


@router.get("/usuario/{user_id}/vistas/count")
def get_vistas_count(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return {"total_vistas": interaccion_repository.count_vistas_by_user(db, user_id)}