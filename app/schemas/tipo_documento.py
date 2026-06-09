from pydantic import BaseModel


class TipoDocumentoResponse(BaseModel):
    id_tipo_doc: int
    siglas: str
    descripcion: str

    model_config = {"from_attributes": True}
