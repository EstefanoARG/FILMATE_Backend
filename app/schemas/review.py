# backend/app/schemas/review.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReviewBase(BaseModel):
    id_pelicula: int
    calificacion_estrellas: float
    comentario: Optional[str] = None


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id_resena: int
    id_usuario: int
    estado_moderacion: str
    fecha_publicacion: datetime

    class Config:
        from_attributes = True