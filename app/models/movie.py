"""Modelo `Pelicula`.

Representa una película en la plataforma Filmate.

Campos principales:
- `id_pelicula`: identificador primario.
- `titulo`: título de la película.
- `sinopsis`: texto con la sinopsis.
- `duracion_minutos`: duración en minutos.
- `clasificacion_edad`: clasificación por edad.
- `url_poster`, `url_trailer`: URLs relacionadas.

Relaciones:
- `generos`: relación con `PeliculaGenero`.
- `actores`: relación con `PeliculaActor`.
- `banners`, `funciones`, `resenas`, `favoritos`.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    DateTime
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Pelicula(Base):
    """Clase ORM que mapea la tabla `pelicula`.

    Use este docstring para describir la intención del modelo y las
    relaciones más importantes; Sphinx lo mostrará en la documentación API.
    """
    __tablename__ = "pelicula"

    id_pelicula = Column(
        Integer,
        primary_key=True
    )

    titulo = Column(
        String(150),
        nullable=False
    )

    sinopsis = Column(Text)

    duracion_minutos = Column(Integer)

    clasificacion_edad = Column(
        String(10)
    )

    url_poster = Column(
        String(255)
    )

    url_trailer = Column(
        String(255)
    )

    categoria_cartelera = Column(
        Enum(
            "Estreno",
            "Preventa",
            "Cartelera",
            "Proximamente",
            name="categoria_cartelera"
        ),
        default="Proximamente"
    )

    estado_registro = Column(
        Enum(
            "Activo",
            "Inactivo",
            name="estado_pelicula"
        ),
        default="Activo"
    )

    fecha_creacion = Column(
        DateTime,
        server_default=func.now()
    )

    generos = relationship(
        "PeliculaGenero",
        back_populates="pelicula"
    )

    actores = relationship(
        "PeliculaActor",
        back_populates="pelicula"
    )

    banners = relationship(
        "BannerHome",
        back_populates="pelicula"
    )

    funciones = relationship(
        "Funcion",
        back_populates="pelicula"
    )

    resenas = relationship(
        "Resena",
        back_populates="pelicula"
    )

    favoritos = relationship(
        "Favorito",
        back_populates="pelicula"
    )