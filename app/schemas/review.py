from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    id_usuario: int
    id_pelicula: int
    puntuacion_estrellas: Optional[int] = None
    comentario: Optional[str] = None


class ReviewResponse(BaseModel):
    id_resena: int
    id_usuario: int
    id_pelicula: int
    puntuacion_estrellas: Optional[int] = None
    comentario: Optional[str] = None
    fecha_publicacion: Optional[datetime] = None

    model_config = {"from_attributes": True}
