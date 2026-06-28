from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Pelicula(Base):
    __tablename__ = "peliculas"

    id_pelicula = Column(Integer, primary_key=True)
    id_tmdb = Column(Integer, unique=True, nullable=True, index=True)
    titulo = Column(String(255), nullable=False)
    anio_lanzamiento = Column(Integer, nullable=False)
    duracion_minutos = Column(Integer, nullable=False)
    clasificacion = Column(String(10), nullable=False)
    estado_pelicula = Column(String(30), nullable=False, default="PRÓXIMAMENTE")
    url_poster = Column(String(255), nullable=False)
    url_banner = Column(String(255))
    url_trailer = Column(String(255))
    sinopsis = Column(Text)
    elenco = Column(Text)
    director = Column(String(150), nullable=False)
    total_vistas_comunidad = Column(Integer, default=0)
    total_favoritos_comunidad = Column(Integer, default=0)
    eliminado = Column(Boolean, nullable=False, default=False)
    fecha_eliminacion = Column(DateTime, default=None)

    generos = relationship(
        "Genero",
        secondary="peliculas_generos",
        primaryjoin="Pelicula.id_pelicula == foreign(PeliculaGenero.id_pelicula)",
        secondaryjoin="Genero.id_genero == foreign(PeliculaGenero.id_genero)",
        viewonly=True
    )
    funciones = relationship("Funcion", back_populates="pelicula")
    resenas = relationship("Resena", back_populates="pelicula")
