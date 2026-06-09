from pydantic import BaseModel
from typing import List, Optional


class CarritoItemCreate(BaseModel):
    id_usuario: int
    id_producto: int
    cantidad: int = 1


class CarritoItemUpdate(BaseModel):
    cantidad: int


class CarritoItemResponse(BaseModel):
    id_carrito: int
    id_usuario: int
    id_producto: int
    cantidad: int

    model_config = {"from_attributes": True}


class CarritoResponse(BaseModel):
    items: List[CarritoItemResponse]
    total: float = 0.0
