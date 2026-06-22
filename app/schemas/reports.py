from typing import List, Optional
from pydantic import BaseModel


class TaquillaItem(BaseModel):
    id: int
    titulo: str
    funciones: int
    entradas: int
    ingreso: float
    estado: str


class TaquillaResumen(BaseModel):
    total_funciones: int
    total_entradas: int
    ingreso_bruto: float
    ticket_promedio: float


class TaquillaResponse(BaseModel):
    data: List[TaquillaItem]
    resumen: TaquillaResumen


class OcupacionItem(BaseModel):
    id_sala: int
    sala: str
    id_cine: int
    cine: str
    capacidad: int
    vendidos: int
    porcentaje: float
    formato: str


class OcupacionResumen(BaseModel):
    total_salas: int
    ocupacion_promedio: float
    capacidad_total: int


class OcupacionResponse(BaseModel):
    data: List[OcupacionItem]
    resumen: OcupacionResumen


class VentaHorarioItem(BaseModel):
    horario: str
    ventas: int
    ingresos: float
    tickets: int


class VentaHorarioResumen(BaseModel):
    horario_pico: str
    ingreso_total: float
    total_tickets: int


class VentaHorarioResponse(BaseModel):
    data: List[VentaHorarioItem]
    resumen: VentaHorarioResumen


class AnalisisItem(BaseModel):
    id_genero: int
    genero: str
    peliculas: int
    funciones: int
    ingresos: float
    porcentaje: float


class AnalisisResumen(BaseModel):
    genero_principal: str
    ingreso_total: float
    total_peliculas: int


class AnalisisResponse(BaseModel):
    data: List[AnalisisItem]
    resumen: AnalisisResumen
