# backend/app/schemas/seat.py

from pydantic import BaseModel
from typing import Optional


class SeatBase(BaseModel):
    id_sala: int
    fila: str
    numero: int
    coord_x: Optional[int] = None
    coord_y: Optional[int] = None


class SeatCreate(SeatBase):
    pass


class SeatResponse(SeatBase):
    id_asiento: int
    estado_fisico: str

    class Config:
        from_attributes = True