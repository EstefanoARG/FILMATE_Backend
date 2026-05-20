# backend/app/models/showtime.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo Funcion.

Representa una función/sesión de proyección en una sala para una película.
"""

class Funcion(Base):
    """Entidad `Funcion`.
    """
    __tablename__ = "funcion"

    id_funcion = Column(
        Integer,
        primary_key=True
    )

    id_pelicula = Column(
        Integer,
        ForeignKey("pelicula.id_pelicula"),
        nullable=False
    )

    id_sala = Column(
        Integer,
        ForeignKey("sala.id_sala"),
        nullable=False
    )

    fecha_hora_inicio = Column(
        DateTime,
        nullable=False
    )

    fecha_hora_fin = Column(
        DateTime,
        nullable=False
    )

    idioma = Column(
        String(50)
    )

    formato = Column(
        String(20)
    )

    pelicula = relationship(
        "Pelicula",
        back_populates="funciones"
    )

    sala = relationship(
        "Sala",
        back_populates="funciones"
    )

    asientos = relationship(
        "FuncionAsiento",
        back_populates="funcion"
    )

    reservas = relationship(
        "Reserva",
        back_populates="funcion"
    )

    boletos = relationship(
        "Boleto",
        back_populates="funcion"
    )