from typing import List, Optional

from pydantic import BaseModel

from app.schemas.ticket import TicketQrPayload


class SnackOrderItem(BaseModel):
    id_producto: int
    cantidad: int


class CheckoutRequest(BaseModel):
    id_usuario: int
    id_funcion: int
    ids_asientos: List[int]
    snacks: List[SnackOrderItem] = []
    monto_confiteria: float = 0.0
    metodo_pago: Optional[str] = None
    token_pago: str
    email: str


class CheckoutResponse(BaseModel):
    id_transaccion: int
    estado_pago: str
    monto_boletos: float
    monto_confiteria: float
    monto_total: float
    boletos: List[dict]
    qr: Optional[TicketQrPayload] = None
    id_cargo_pasarela: Optional[str] = None
