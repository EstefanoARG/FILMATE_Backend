from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Asiento(Base):
    __tablename__ = "asientos"

    id_asiento = Column(Integer, primary_key=True)
    id_sala = Column(Integer, ForeignKey("salas.id_sala", ondelete="CASCADE"), nullable=False)
    fila = Column(String(5), nullable=False)
    columna = Column(Integer, nullable=False)
    tipo_asiento = Column(String(20), default="Regular")
    estado_asiento = Column(String(20), nullable=False, default="Activo")
    eliminado = Column(Boolean, nullable=False, default=False)
    fecha_eliminacion = Column(DateTime, default=None)

    sala = relationship("Sala", back_populates="asientos")
    funciones = relationship("AsientoFuncion", back_populates="asiento")
