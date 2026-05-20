from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DECIMAL
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo ReservaSnack.

Asociación de productos de snack dentro de una reserva.
"""

class ReservaSnack(Base):
    """Entidad `ReservaSnack`.
    """
    __tablename__ = "reserva_snack"

    id_reserva = Column(
        Integer,
        ForeignKey("reserva.id_reserva"),
        primary_key=True
    )

    id_producto = Column(
        Integer,
        ForeignKey("producto_snack.id_producto"),
        primary_key=True
    )

    cantidad = Column(Integer, nullable=False)

    precio_unitario = Column(
        DECIMAL(8, 2),
        nullable=False
    )

    reserva = relationship(
        "Reserva",
        back_populates="snacks"
    )

    producto = relationship(
        "ProductoSnack",
        back_populates="reservas"
    )