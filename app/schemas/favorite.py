# backend/app/schemas/favorite.py

from pydantic import BaseModel
from datetime import datetime


class FavoriteBase(BaseModel):
    id_pelicula: int


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteResponse(FavoriteBase):
    id_usuario: int
    fecha_agregado: datetime

    class Config:
        from_attributes = True