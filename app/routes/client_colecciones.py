import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.coleccion import Coleccion
from app.repositories import coleccion_repository
from app.schemas.coleccion import ColeccionCreate, ColeccionResponse, AgregarPeliculaColeccion

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/colecciones", tags=["client colecciones"])

@router.get("/usuario/{user_id}", response_model=List[ColeccionResponse])
def list_colecciones(user_id: int, db: Session = Depends(get_db)):
    return coleccion_repository.list_colecciones(db, user_id)

@router.post("/", response_model=ColeccionResponse, status_code=201)
def create_coleccion(payload: ColeccionCreate, db: Session = Depends(get_db)):
    coleccion = Coleccion(
        id_usuario=payload.id_usuario,
        titulo_coleccion=payload.titulo_coleccion,
        descripcion=payload.descripcion,
    )
    return coleccion_repository.create_coleccion(db, coleccion)

@router.post("/agregar-pelicula")
def add_pelicula(payload: AgregarPeliculaColeccion, db: Session = Depends(get_db)):
    coleccion_repository.add_pelicula_to_coleccion(db, payload.id_coleccion, payload.id_pelicula)
    return {"message": "Película agregada a la colección"}

@router.delete("/{coleccion_id}/pelicula/{pelicula_id}")
def remove_pelicula(coleccion_id: int, pelicula_id: int, db: Session = Depends(get_db)):
    removed = coleccion_repository.remove_pelicula_from_coleccion(db, coleccion_id, pelicula_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return {"message": "Película removida de la colección"}