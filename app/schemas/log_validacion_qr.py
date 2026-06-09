from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LogValidacionQrResponse(BaseModel):
    id_log: int
    ticket_escaneado: str
    fecha_escaneo: Optional[datetime] = None
    resultado_validacion: str
    id_usuario_control: Optional[int] = None

    model_config = {"from_attributes": True}
