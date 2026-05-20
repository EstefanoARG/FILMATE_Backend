# backend/app/models/showtime_seat.py

from sqlalchemy import (
    Column,
    Integer,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo FuncionAsiento.

Asociación entre funciones y asientos con estado por función.
"""

class FuncionAsiento(Base):
    """Entidad `FuncionAsiento`.
    """
    __tablename__ = "funcion_asiento"

    id_funcion = Column(
        Integer,
        ForeignKey("funcion.id_funcion"),
        primary_key=True
    )

    id_asiento = Column(
        Integer,
        ForeignKey("asiento.id_asiento"),
        primary_key=True
    )

    estado = Column(
        Enum(
            "Disponible",
            "Reservado",
            "Vendido",
            name="estado_funcion_asiento"
        ),
        default="Disponible"
    )

    funcion = relationship(
        "Funcion",
        back_populates="asientos"
    )

    asiento = relationship(
        "Asiento",
        back_populates="funciones"
    )