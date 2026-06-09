from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ColeccionPelicula(Base):
    __tablename__ = "colecciones_peliculas"

    id_coleccion = Column(Integer, ForeignKey("colecciones.id_coleccion", ondelete="CASCADE"), primary_key=True)
    id_pelicula = Column(Integer, ForeignKey("peliculas.id_pelicula", ondelete="RESTRICT"), primary_key=True)

    coleccion = relationship("Coleccion", back_populates="peliculas")
