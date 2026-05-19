# backend/app/models/room.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class Sala(Base):
    __tablename__ = "sala"

    id_sala = Column(
        Integer,
        primary_key=True
    )

    id_cine = Column(
        Integer,
        ForeignKey("cine.id_cine"),
        nullable=False
    )

    nombre = Column(
        String(50),
        nullable=False
    )

    formato_sala = Column(
        String(20)
    )

    capacidad_total = Column(
        Integer,
        nullable=False
    )

    cine = relationship(
        "Cine",
        back_populates="salas"
    )

    asientos = relationship(
        "Asiento",
        back_populates="sala"
    )

    funciones = relationship(
        "Funcion",
        back_populates="sala"
    )