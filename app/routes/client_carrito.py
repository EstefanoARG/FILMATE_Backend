import logging
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.repositories import carrito_repository
from app.schemas.carrito_confiteria import CarritoItemCreate, CarritoItemUpdate, CarritoItemResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/carrito", tags=["client carrito"])

@router.get("/{user_id}", response_model=List[CarritoItemResponse])
def get_carrito(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return carrito_repository.get_carrito(db, user_id)

@router.post("/", response_model=CarritoItemResponse, status_code=201)
def add_to_carrito(payload: CarritoItemCreate, db: Annotated[Session, Depends(get_db)]):
    return carrito_repository.add_item(db, payload.id_usuario, payload.id_producto, payload.cantidad)

@router.put("/{carrito_id}", response_model=CarritoItemResponse, responses={404: {"description": "Item no encontrado"}})
def update_carrito_item(carrito_id: int, payload: CarritoItemUpdate, db: Annotated[Session, Depends(get_db)]):
    item = carrito_repository.update_item_cantidad(db, carrito_id, payload.cantidad)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item

@router.delete("/{carrito_id}", responses={404: {"description": "Item no encontrado"}})
def remove_from_carrito(carrito_id: int, db: Annotated[Session, Depends(get_db)]):
    removed = carrito_repository.remove_item(db, carrito_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"message": "Item removido del carrito"}