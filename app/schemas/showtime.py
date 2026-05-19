# backend/app/schemas/showtime.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ShowtimeBase(BaseModel):
    id_pelicula: int
    id_sala: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    idioma: Optional[str] = None
    formato: Optional[str] = None


class ShowtimeCreate(ShowtimeBase):
    pass


class ShowtimeResponse(ShowtimeBase):
    id_funcion: int

    class Config:
        from_attributes = True