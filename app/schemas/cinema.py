# backend/app/schemas/cinema.py

from pydantic import BaseModel
from typing import Optional


class CinemaBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    ciudad: Optional[str] = None


class CinemaCreate(CinemaBase):
    pass


class CinemaResponse(CinemaBase):
    id_cine: int
    estado: bool

    class Config:
        from_attributes = True