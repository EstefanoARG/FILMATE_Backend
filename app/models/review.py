# backend/app/models/review.py

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    DateTime,
    DECIMAL,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

"""Modelo Resena.

Reseñas de usuarios para películas con calificación y comentario.
"""

class Resena(Base):
    """Entidad `Resena`.
    """
    __tablename__ = "resena"

    id_resena = Column(
        Integer,
        primary_key=True
    )

    id_usuario = Column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        nullable=False
    )

    id_pelicula = Column(
        Integer,
        ForeignKey("pelicula.id_pelicula"),
        nullable=False
    )

    calificacion_estrellas = Column(
        DECIMAL(2, 1),
        nullable=False
    )

    comentario = Column(Text)

    estado_moderacion = Column(
        Enum(
            "Aprobado",
            "Pendiente",
            "Oculto",
            name="estado_moderacion"
        ),
        default="Aprobado"
    )

    fecha_publicacion = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="resenas"
    )

    pelicula = relationship(
        "Pelicula",
        back_populates="resenas"
    )