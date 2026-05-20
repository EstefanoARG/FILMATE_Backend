"""Modelo Actor.

Define la entidad `Actor` con sus campos básicos y la relación con
películas a través de `PeliculaActor`. Estos docstrings ayudan a que la
documentación muestre la intención del modelo y sus relaciones.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Actor(Base):
    """Representa un actor o actriz.

    Atributos:
    - `id_actor`: PK del actor.
    - `nombre`: nombre completo.
    - `peliculas`: relación con tabla de asociación `PeliculaActor`.
    """
    __tablename__ = "actor"

    id_actor = Column(
        Integer,
        primary_key=True
    )

    nombre = Column(
        String(100),
        nullable=False
    )

    peliculas = relationship(
        "PeliculaActor",
        back_populates="actor"
    )