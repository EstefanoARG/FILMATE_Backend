from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class BloqueoTemporalRequest(BaseModel):
    id_usuario: int
    id_funcion: int
    ids_asientos: List[int]


class BloqueoTemporalResponse(BaseModel):
    id_funcion: int
    ids_asientos_bloqueados: List[int]
    expira_en: Optional[datetime] = None

    model_config = {"from_attributes": True}
