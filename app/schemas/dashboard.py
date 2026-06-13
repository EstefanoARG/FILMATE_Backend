from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel


class VentaPorDia(BaseModel):
    dia: date
    ventas: int


class PeliculaTaquillera(BaseModel):
    titulo: str
    total: float


class IngresoPorFormato(BaseModel):
    tipo_formato: str
    total: float


class ComparacionItem(BaseModel):
    actual: float
    anterior: float
    cambioPorcentual: float


class ComparacionPeriodo(BaseModel):
    ventas: ComparacionItem
    ingresos: ComparacionItem
    nuevosUsuarios: ComparacionItem


class DashboardResponse(BaseModel):
    ventasPorDia: List[VentaPorDia]
    peliculaMasTaquillera: Optional[PeliculaTaquillera] = None
    ocupacionPromedio: float
    ingresosPorFormato: List[IngresoPorFormato]
    nuevosUsuarios: int
    comparacion: ComparacionPeriodo
