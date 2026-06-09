from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TransaccionResponse(BaseModel):
    id_transaccion: int
    id_usuario: int
    id_funcion: int
    monto_boletos: float
    monto_confiteria: float
    monto_total: float
    estado_pago: str
    metodo_pago: Optional[str] = None
    fecha_transaccion: Optional[datetime] = None

    model_config = {"from_attributes": True}
