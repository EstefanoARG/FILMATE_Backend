# backend/app/models/actor.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Actor(Base):
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