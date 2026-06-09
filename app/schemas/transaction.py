from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class TransactionItem(BaseModel):
    id_transaccion: int
    cliente: str
    pelicula: str
    sala: str
    monto_total: float
    estado_pago: str
    metodo_pago: Optional[str] = None
    fecha_transaccion: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TransactionMetrics(BaseModel):
    ventasMes: float
    ingresosTotales: float
    reembolsos: int
    ticketPromedio: float


class TransactionListResponse(BaseModel):
    data: List[TransactionItem]
    total: int
    page: int
    totalPages: int
    metricas: TransactionMetrics


class TransactionDetail(BaseModel):
    id_transaccion: int
    cliente: str
    correo: str
    pelicula: str
    sala: str
    monto_boletos: float
    monto_confiteria: float
    monto_total: float
    estado_pago: str
    metodo_pago: Optional[str] = None
    fecha_transaccion: Optional[datetime] = None
    boletos: List[dict] = []
    snacks: List[dict] = []

    model_config = {"from_attributes": True}


class ValidateQRSchema(BaseModel):
    codigo_qr_token: Optional[str] = None
    codigo: Optional[str] = None


class ValidateResponse(BaseModel):
    valido: bool
    estado: str
    detalle: Optional[dict] = None
