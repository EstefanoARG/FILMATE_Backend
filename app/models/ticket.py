# backend/app/models/ticket.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DECIMAL,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo Boleto.

Representa un boleto generado para una reserva y función específica.
"""

class Boleto(Base):
    """Entidad `Boleto` con referencias a `Reserva`, `Funcion`, `Asiento` y `Tarifa`.
    """
    __tablename__ = "boleto"

    id_boleto = Column(
        Integer,
        primary_key=True
    )

    id_reserva = Column(
        Integer,
        ForeignKey("reserva.id_reserva"),
        nullable=False
    )

    id_funcion = Column(
        Integer,
        ForeignKey("funcion.id_funcion"),
        nullable=False
    )

    id_asiento = Column(
        Integer,
        ForeignKey("asiento.id_asiento"),
        nullable=False
    )

    id_tarifa = Column(
        Integer,
        ForeignKey("tarifa.id_tarifa"),
        nullable=False
    )

    codigo_qr = Column(
        String(255),
        unique=True,
        nullable=False
    )

    precio_pagado = Column(
        DECIMAL(8, 2),
        nullable=False
    )

    estado_ingreso = Column(
        Enum(
            "Vigente",
            "Usado",
            name="estado_ingreso"
        ),
        default="Vigente"
    )

    reserva = relationship(
        "Reserva",
        back_populates="boletos"
    )

    funcion = relationship(
        "Funcion",
        back_populates="boletos"
    )

    asiento = relationship(
        "Asiento",
        back_populates="boletos"
    )

    tarifa = relationship(
        "Tarifa",
        back_populates="boletos"
    )