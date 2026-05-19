# backend/app/schemas/promotion.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PromotionBase(BaseModel):
    codigo_cupon: str
    porcentaje_descuento: Optional[float] = None
    monto_descuento: Optional[float] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    limite_usos: Optional[int] = None


class PromotionCreate(PromotionBase):
    pass


class PromotionResponse(PromotionBase):
    id_promocion: int

    class Config:
        from_attributes = True