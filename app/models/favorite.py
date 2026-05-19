# backend/app/models/favorite.py

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Favorito(Base):
    __tablename__ = "favorito"

    id_usuario = Column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        primary_key=True
    )

    id_pelicula = Column(
        Integer,
        ForeignKey("pelicula.id_pelicula"),
        primary_key=True
    )

    fecha_agregado = Column(
        DateTime,
        server_default=func.now()
    )

    usuario = relationship(
        "Usuario",
        back_populates="favoritos"
    )

    pelicula = relationship(
        "Pelicula",
        back_populates="favoritos"
    )