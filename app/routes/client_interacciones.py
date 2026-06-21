import logging
from typing import List, Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.repositories import interaccion_repository
from app.schemas.interaccion_pelicula import InteraccionPeliculaCreate, InteraccionPeliculaResponse
from app.models.interaccion_pelicula import InteraccionPelicula

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/interacciones", tags=["client interacciones"])

# Schema para recibir el array del front
class TopFavoritesUpdate(BaseModel):
    movie_ids: List[int]

@router.post("/", response_model=InteraccionPeliculaResponse)
def upsert_interaccion(payload: InteraccionPeliculaCreate, db: Annotated[Session, Depends(get_db)]):
    data = payload.model_dump(exclude={"id_usuario", "id_pelicula"})
    return interaccion_repository.upsert_interaccion(db, payload.id_usuario, payload.id_pelicula, data)

@router.get("/usuario/{user_id}")
def list_interacciones(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return interaccion_repository.list_interacciones_by_user(db, user_id)

@router.put("/usuario/{user_id}/favorite-movies", responses={400: {"description": "Maximo 5 películas permitidas"}})
def update_top_favorites(user_id: int, payload: TopFavoritesUpdate, db: Annotated[Session, Depends(get_db)]):
    """Guarda el Top 5 ordenado manipulando los timestamps (Hack sin modificar BD)"""
    if len(payload.movie_ids) > 5:
        raise HTTPException(status_code=400, detail="Máximo 5 películas permitidas")

    # Limpiamos favoritos para reordenar
    db.query(InteraccionPelicula).filter(InteraccionPelicula.id_usuario == user_id).update({"favorita": False, "fecha_favorito": None})
    
    ahora = datetime.now()
    for index, movie_id in enumerate(payload.movie_ids):
        # Asignamos tiempo artificial para forzar el orden DESC
        artificial_time = ahora + timedelta(seconds=(5 - index))
        interaccion = db.query(InteraccionPelicula).filter_by(id_usuario=user_id, id_pelicula=movie_id).first()
        
        if not interaccion:
            nueva_interaccion = InteraccionPelicula(id_usuario=user_id, id_pelicula=movie_id, favorita=True, fecha_favorito=artificial_time)
            db.add(nueva_interaccion)
        else:
            interaccion.favorita = True
            interaccion.fecha_favorito = artificial_time
            
    db.commit()
    return {"message": "Top 5 actualizado y ordenado correctamente"}