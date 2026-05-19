# backend/app/schemas/reservation.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ReservationBase(BaseModel):
    id_funcion: int
    id_promocion: Optional[int] = None
    fecha_expiracion: datetime
    monto_subtotal: float
    descuento_aplicado: float
    monto_total: float
    metodo_pago: Optional[str] = None


class ReservationCreate(ReservationBase):
    pass


class ReservationResponse(ReservationBase):
    id_reserva: int
    id_usuario: int
    fecha_reserva: datetime
    estado_pago: str
    transaccion_id: Optional[str] = None

    class Config:
        from_attributes = True