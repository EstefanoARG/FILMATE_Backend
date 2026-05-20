# backend/app/models/tariff.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    Enum
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo Tarifa.

Define tarifas aplicables a boletos según nombre, precio y días.
"""

class Tarifa(Base):
    """Entidad `Tarifa`.
    """
    __tablename__ = "tarifa"

    id_tarifa = Column(
        Integer,
        primary_key=True
    )

    nombre = Column(
        String(50),
        nullable=False
    )

    precio = Column(
        DECIMAL(8, 2),
        nullable=False
    )

    dia_aplica = Column(
        Enum(
            "Lunes",
            "Martes",
            "Miercoles",
            "Jueves",
            "Viernes",
            "Sabado",
            "Domingo",
            "Todos",
            name="dia_tarifa"
        ),
        default="Todos"
    )

    boletos = relationship(
        "Boleto",
        back_populates="tarifa"
    )