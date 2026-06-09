from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class PeliculaGenero(Base):
    __tablename__ = "peliculas_generos"

    id_pelicula = Column(Integer, ForeignKey("peliculas.id_pelicula", ondelete="CASCADE"), primary_key=True)
    id_genero = Column(Integer, ForeignKey("generos.id_genero", ondelete="CASCADE"), primary_key=True)
