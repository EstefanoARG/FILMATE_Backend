# backend/app/models/banner.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class BannerHome(Base):
    __tablename__ = "banner_home"

    id_banner = Column(
        Integer,
        primary_key=True
    )

    id_pelicula = Column(
        Integer,
        ForeignKey("pelicula.id_pelicula")
    )

    imagen_url = Column(
        String(255),
        nullable=False
    )

    orden = Column(
        Integer,
        nullable=False
    )

    is_activo = Column(
        Boolean,
        default=True
    )

    pelicula = relationship(
        "Pelicula",
        back_populates="banners"
    )