# backend/app/models/movie_genre.py

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo PeliculaGenero.

Asociación entre películas y géneros.
"""

class PeliculaGenero(Base):
    """Entidad `PeliculaGenero`.
    """
    __tablename__ = "pelicula_genero"

    id_pelicula = Column(
        Integer,
        ForeignKey("pelicula.id_pelicula"),
        primary_key=True
    )

    id_genero = Column(
        Integer,
        ForeignKey("genero.id_genero"),
        primary_key=True
    )

    pelicula = relationship(
        "Pelicula",
        back_populates="generos"
    )

    genero = relationship(
        "Genero",
        back_populates="peliculas"
    )