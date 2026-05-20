# backend/app/models/reservation.py
from __future__ import annotations

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    DECIMAL,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

"""Modelo Reserva.

Reserva de boletos y snacks realizada por un usuario para una función.
"""

class Reserva(Base):
    """Entidad `Reserva`.
    """
    __tablename__ = "reserva"

    id_reserva = Column(
        Integer,
        primary_key=True
    )

    id_usuario = Column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    id_funcion = Column(
        Integer,
        ForeignKey("funcion.id_funcion"),
        nullable=False
    )

    id_promocion = Column(
        Integer,
        ForeignKey("promocion.id_promocion")
    )

    fecha_reserva = Column(
        DateTime,
        server_default=func.now()
    )

    fecha_expiracion = Column(
        DateTime,
        nullable=False
    )

    monto_subtotal = Column(
        DECIMAL(10, 2),
        nullable=False
    )

    descuento_aplicado = Column(
        DECIMAL(10, 2),
        default=0
    )

    monto_total = Column(
        DECIMAL(10, 2),
        nullable=False
    )

    estado_pago = Column(
        Enum(
            "Pendiente",
            "Pagado",
            "Cancelado",
            "Reembolsado",
            name="estado_pago"
        ),
        default="Pendiente"
    )

    metodo_pago = Column(
        String(50)
    )

    transaccion_id = Column(
        String(100)
    )

    usuario = relationship(
        "Usuario",
        back_populates="reservas"
    )

    funcion = relationship(
        "Funcion",
        back_populates="reservas"
    )

    promocion = relationship(
        "Promocion",
        back_populates="reservas"
    )

    boletos = relationship(
        "Boleto",
        back_populates="reserva"
    )
    snacks = relationship(
        "ReservaSnack",
        back_populates="reserva"
    )