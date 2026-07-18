from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class VentaPorDia(BaseModel):
    dia: str
    ventas: int


class PeliculaTaquillera(BaseModel):
    titulo: str
    total: float


class IngresoPorFormato(BaseModel):
    tipo_formato: str
    total: float


class IngresoPorCategoria(BaseModel):
    tipo_sala: str
    total: float


class ComparacionItem(BaseModel):
    actual: float
    anterior: float
    cambioPorcentual: float


class ComparacionPeriodo(BaseModel):
    ventas: ComparacionItem
    ingresos: ComparacionItem
    nuevosUsuarios: ComparacionItem


class DashboardSala(BaseModel):
    id_sala: int
    id_cine: int | None = None
    nombre_sala: str
    tipo_sala: str | None = None
    capacidad_asientos: int | None = 0
    nombre_cine: str | None = None


class DashboardTransaccion(BaseModel):
    id_transaccion: int
    cliente: str | None = None
    pelicula: str | None = None
    sala: str | None = None
    monto_total: float
    estado_pago: str
    metodo_pago: str | None = None
    fecha_transaccion: datetime | None = None
    tipo: str | None = None


class DashboardResponse(BaseModel):
    ventasPorDia: List[VentaPorDia]
    peliculaMasTaquillera: Optional[PeliculaTaquillera] = None
    ocupacionPromedio: float
    ingresosPorFormato: List[IngresoPorFormato]
    ingresosPorCategoria: List[IngresoPorCategoria]
    nuevosUsuarios: int
    ventasMes: int = 0
    ultimasTransacciones: List[DashboardTransaccion] = []
    salas: List[DashboardSala] = []
    comparacion: ComparacionPeriodo
