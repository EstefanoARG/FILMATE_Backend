# backend/app/models/genre.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo Genero.

Género de película (ej. Acción, Drama).
"""

class Genero(Base):
    """Entidad `Genero`.
    """
    __tablename__ = "genero"

    id_genero = Column(
        Integer,
        primary_key=True
    )

    nombre = Column(
        String(50),
        unique=True,
        nullable=False
    )

    peliculas = relationship(
        "PeliculaGenero",
        back_populates="genero"
    )