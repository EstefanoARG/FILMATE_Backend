from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

from app.schemas.transaccion import TransaccionResponse
from app.schemas.ticket import BoletaTicketResponse


class ReservationResponse(BaseModel):
    transaccion: TransaccionResponse
    boletos: List[BoletaTicketResponse]

    model_config = {"from_attributes": True}
