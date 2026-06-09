from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Sala(Base):
    __tablename__ = "salas"

    id_sala = Column(Integer, primary_key=True)
    id_cine = Column(Integer, ForeignKey("cines.id_cine", ondelete="CASCADE"), nullable=False)
    nombre_sala = Column(String(50), nullable=False)
    tipo_sala = Column(String(20), nullable=False, default="Stand.")
    tipo_formato = Column(String(20), nullable=False)
    capacidad_asientos = Column(Integer, nullable=False, default=0)
    estado_sala = Column(String(20), nullable=False, default="Activa")
    eliminado = Column(Boolean, nullable=False, default=False)
    fecha_eliminacion = Column(DateTime, default=None)

    cine = relationship("Cine", back_populates="salas")
    asientos = relationship("Asiento", back_populates="sala")
    funciones = relationship("Funcion", back_populates="sala")
