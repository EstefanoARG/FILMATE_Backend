from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import payment_gateway_service

router = APIRouter(prefix="/client/payments", tags=["client payments"])


class TokenizeCardRequest(BaseModel):
    numero_tarjeta: str
    cvv: str
    mes_expiracion: int
    anio_expiracion: int
    titular: str


class TokenizeYapeRequest(BaseModel):
    celular: str
    codigo_otp: str


class TokenResponse(BaseModel):
    token: Optional[str] = None
    marca: Optional[str] = None
    error: Optional[str] = None


@router.get("/metodos-prueba")
def get_metodos_prueba():
    """Catálogo de tarjetas/números de Yape de prueba y el resultado que simulan."""
    return payment_gateway_service.listar_metodos_prueba()


@router.post("/tokenize/tarjeta", response_model=TokenResponse)
def tokenize_tarjeta(payload: TokenizeCardRequest):
    return payment_gateway_service.tokenizar_tarjeta(
        payload.numero_tarjeta, payload.cvv, payload.mes_expiracion, payload.anio_expiracion, payload.titular
    )


@router.post("/tokenize/yape", response_model=TokenResponse)
def tokenize_yape(payload: TokenizeYapeRequest):
    return payment_gateway_service.tokenizar_yape(payload.celular, payload.codigo_otp)
