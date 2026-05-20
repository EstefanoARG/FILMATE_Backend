# backend/app/models/seat.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo Asiento.

Define la posición y estado físico de un asiento en una sala.
"""

class Asiento(Base):
    """Entidad `Asiento`.
    """
    __tablename__ = "asiento"

    id_asiento = Column(
        Integer,
        primary_key=True
    )

    id_sala = Column(
        Integer,
        ForeignKey("sala.id_sala"),
        nullable=False
    )

    fila = Column(
        String(5),
        nullable=False
    )

    numero = Column(
        Integer,
        nullable=False
    )

    coord_x = Column(Integer)

    coord_y = Column(Integer)

    estado_fisico = Column(
        Enum(
            "Disponible",
            "Mantenimiento",
            "Inhabilitado",
            name="estado_fisico"
        ),
        default="Disponible"
    )

    sala = relationship(
        "Sala",
        back_populates="asientos"
    )

    funciones = relationship(
        "FuncionAsiento",
        back_populates="asiento"
    )

    boletos = relationship(
        "Boleto",
        back_populates="asiento"
    )