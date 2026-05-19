from pydantic import BaseModel


class ReservationSnackBase(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float


class ReservationSnackCreate(ReservationSnackBase):
    pass


class ReservationSnackResponse(ReservationSnackBase):
    id_reserva: int

    class Config:
        from_attributes = True