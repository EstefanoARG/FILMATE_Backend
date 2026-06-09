from pydantic import BaseModel
from typing import Optional


class RolResponse(BaseModel):
    id_role: int
    nombre_rol: str
    descripcion: Optional[str] = None

    model_config = {"from_attributes": True}
