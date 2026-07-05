from typing import List, Optional
from pydantic import BaseModel


class PrecioFormatoItem(BaseModel):
    formato: str
    precio: float


class PreciosFormatoRequest(BaseModel):
    precios: List[PrecioFormatoItem]


class PreciosFormatoResponse(BaseModel):
    precios: List[PrecioFormatoItem]


class PrecioSalaFormatoItem(BaseModel):
    tipo_sala: str
    formato: str
    precio: float


class PreciosSalaFormatoRequest(BaseModel):
    precios: List[PrecioSalaFormatoItem]


class PreciosSalaFormatoResponse(BaseModel):
    precios: List[PrecioSalaFormatoItem]


class TipoEntradaItem(BaseModel):
    id: str
    tipo: str
    porcentaje: int


class TiposEntradaRequest(BaseModel):
    tipos: List[TipoEntradaItem]


class TiposEntradaResponse(BaseModel):
    tipos: List[TipoEntradaItem]


class ConfiteriaProductoItem(BaseModel):
    id: int
    nombre: str
    precio: float


class ConfiteriaListResponse(BaseModel):
    productos: List[ConfiteriaProductoItem]


class ConfiteriaCreateRequest(BaseModel):
    nombre: str
    precio: float
    id_categoria_confi: Optional[int] = 1


class ConfiteriaUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None


class ParametroSistemaItem(BaseModel):
    clave: str
    valor: str
    descripcion: Optional[str] = None
    tipo_dato: str
    categoria: str
    activo: bool


class ParametrosListResponse(BaseModel):
    params: List[ParametroSistemaItem]


class ParametroUpdateRequest(BaseModel):
    valor: str
