# backend/app/models/movie_actor.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo PeliculaActor.

Tabla de asociación entre Pelicula y Actor con el nombre de personaje.
"""

class PeliculaActor(Base):
    """Entidad `PeliculaActor`.
    """
    __tablename__ = "pelicula_actor"

    id_pelicula = Column(
        Integer,
        ForeignKey("pelicula.id_pelicula"),
        primary_key=True
    )

    id_actor = Column(
        Integer,
        ForeignKey("actor.id_actor"),
        primary_key=True
    )

    personaje = Column(
        String(100),
        nullable=False
    )

    pelicula = relationship(
        "Pelicula",
        back_populates="actores"
    )

    actor = relationship(
        "Actor",
        back_populates="peliculas"
    )