# backend/app/schemas/ticket.py

from pydantic import BaseModel


class TicketBase(BaseModel):
    id_reserva: int
    id_funcion: int
    id_asiento: int
    id_tarifa: int
    precio_pagado: float


class TicketCreate(TicketBase):
    pass


class TicketResponse(TicketBase):
    id_boleto: int
    codigo_qr: str
    estado_ingreso: str

    class Config:
        from_attributes = True