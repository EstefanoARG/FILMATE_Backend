# backend/app/schemas/tariff.py

from pydantic import BaseModel


class TariffBase(BaseModel):
    nombre: str
    precio: float
    dia_aplica: str


class TariffCreate(TariffBase):
    pass


class TariffResponse(TariffBase):
    id_tarifa: int

    class Config:
        from_attributes = True