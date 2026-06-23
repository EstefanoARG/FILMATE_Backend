import logging
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.coleccion import Coleccion
from app.repositories import coleccion_repository
from app.schemas.coleccion import (
    ColeccionCreate,
    ColeccionUpdate,
    ColeccionResponse,
    ColeccionDetailResponse,
    PeliculaEnColeccion,
    AgregarPeliculaColeccion,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/colecciones", tags=["client colecciones"])

@router.get("/{coleccion_id}", response_model=ColeccionDetailResponse, responses={404: {"description": "Colección no encontrada"}})
def get_coleccion_detail(coleccion_id: int, db: Annotated[Session, Depends(get_db)]):
    result = coleccion_repository.get_coleccion_detail(db, coleccion_id)
    if not result:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    coleccion, peliculas = result
    return ColeccionDetailResponse(
        id_coleccion=coleccion.id_coleccion,
        id_usuario=coleccion.id_usuario,
        titulo_coleccion=coleccion.titulo_coleccion,
        descripcion=coleccion.descripcion,
        fecha_creacion=coleccion.fecha_creacion,
        peliculas=[PeliculaEnColeccion(id_pelicula=p.id_pelicula, titulo=p.titulo, url_poster=p.url_poster) for p in peliculas],
    )


@router.get("/{coleccion_id}/peliculas", responses={404: {"description": "Colección no encontrada"}})
def get_coleccion_peliculas(coleccion_id: int, db: Annotated[Session, Depends(get_db)]):
    coleccion = coleccion_repository.get_coleccion(db, coleccion_id)
    if not coleccion:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    peliculas = coleccion_repository.get_peliculas_from_coleccion(db, coleccion_id)
    return [PeliculaEnColeccion(id_pelicula=p.id_pelicula, titulo=p.titulo, url_poster=p.url_poster) for p in peliculas]


@router.get("/usuario/{user_id}", response_model=List[ColeccionResponse])
def list_colecciones(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return coleccion_repository.list_colecciones(db, user_id)

@router.post("/", response_model=ColeccionResponse, status_code=201)
def create_coleccion(payload: ColeccionCreate, db: Annotated[Session, Depends(get_db)]):
    coleccion = Coleccion(
        id_usuario=payload.id_usuario,
        titulo_coleccion=payload.titulo_coleccion,
        descripcion=payload.descripcion,
    )
    return coleccion_repository.create_coleccion(db, coleccion)

@router.post("/agregar-pelicula")
def add_pelicula(payload: AgregarPeliculaColeccion, db: Annotated[Session, Depends(get_db)]):
    coleccion_repository.add_pelicula_to_coleccion(db, payload.id_coleccion, payload.id_pelicula)
    return {"message": "Película agregada a la colección"}

@router.put("/{coleccion_id}", response_model=ColeccionResponse, responses={404: {"description": "Colección no encontrada"}})
def update_coleccion(coleccion_id: int, payload: ColeccionUpdate, db: Annotated[Session, Depends(get_db)]):
    updated = coleccion_repository.update_coleccion(db, coleccion_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return updated


@router.delete("/{coleccion_id}", responses={404: {"description": "Colección no encontrada"}})
def delete_coleccion(coleccion_id: int, db: Annotated[Session, Depends(get_db)]):
    deleted = coleccion_repository.soft_delete_coleccion(db, coleccion_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    return {"message": "Colección eliminada"}


@router.delete("/{coleccion_id}/pelicula/{pelicula_id}", responses={404: {"description": "Relación no encontrada"}})
def remove_pelicula(coleccion_id: int, pelicula_id: int, db: Annotated[Session, Depends(get_db)]):
    removed = coleccion_repository.remove_pelicula_from_coleccion(db, coleccion_id, pelicula_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return {"message": "Película removida de la colección"}