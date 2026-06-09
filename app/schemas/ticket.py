from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TicketIssueRequest(BaseModel):
    id_usuario: int
    id_funcion: int
    ids_asientos: List[int]
    metodo_pago: Optional[str] = None


class BoletaTicketResponse(BaseModel):
    id_ticket: int
    id_transaccion: int
    codigo_qr_token: str
    estado_ticket: str
    fecha_emision: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DetalleBoletaAsientoResponse(BaseModel):
    id_detalle_asiento: int
    id_transaccion: int
    id_asiento: int
    ingresado: bool
    fecha_ingreso: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TicketQrPayload(BaseModel):
    version: str
    generado_en: datetime
    transaccion: Dict[str, Any]
    boletos: List[Dict[str, Any]]
    payload_json: str


class TicketIssueResponse(BaseModel):
    transaccion: Dict[str, Any]
    boletos: List[BoletaTicketResponse]
    snacks: List[Dict[str, Any]] = []
    qr: TicketQrPayload
