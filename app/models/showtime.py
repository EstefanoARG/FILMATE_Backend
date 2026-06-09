from sqlalchemy import Column, Integer, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Funcion(Base):
    __tablename__ = "funciones"

    id_funcion = Column(Integer, primary_key=True)
    id_pelicula = Column(Integer, ForeignKey("peliculas.id_pelicula", ondelete="RESTRICT"))
    id_sala = Column(Integer, ForeignKey("salas.id_sala", ondelete="CASCADE"))
    fecha_hora = Column(DateTime, nullable=False)
    precio_base = Column(DECIMAL(10, 2), nullable=False)

    pelicula = relationship("Pelicula", back_populates="funciones")
    sala = relationship("Sala", back_populates="funciones")
    asientos = relationship("AsientoFuncion", back_populates="funcion")
