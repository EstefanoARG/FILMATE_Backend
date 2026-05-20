# backend/app/models/cinema.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo Cine.

Información del cine físico: nombre, dirección y salas.
"""

class Cine(Base):
    """Entidad `Cine`.
    """
    __tablename__ = "cine"

    id_cine = Column(
        Integer,
        primary_key=True
    )

    nombre = Column(
        String(100),
        nullable=False
    )

    direccion = Column(
        String(200)
    )

    ciudad = Column(
        String(100)
    )

    estado = Column(
        Boolean,
        default=True
    )

    salas = relationship(
        "Sala",
        back_populates="cine"
    )