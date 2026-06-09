from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SolicitudReembolsoCreate(BaseModel):
    id_transaccion: int
    motivo: str
    tipo_reembolso: str = "Reembolso total"
    monto_reembolsado: float = 0.00


class SolicitudReembolsoUpdate(BaseModel):
    estado_solicitud: Optional[str] = None
    comentario_administrador: Optional[str] = None
    fecha_resolucion: Optional[datetime] = None


class SolicitudReembolsoResponse(BaseModel):
    id_reembolso: int
    id_transaccion: int
    motivo: str
    tipo_reembolso: str
    monto_reembolsado: float
    estado_solicitud: str
    comentario_administrador: Optional[str] = None
    fecha_solicitud: Optional[datetime] = None
    fecha_resolucion: Optional[datetime] = None

    model_config = {"from_attributes": True}
