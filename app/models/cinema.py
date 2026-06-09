from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cine(Base):
    __tablename__ = "cines"

    id_cine = Column(Integer, primary_key=True)
    nombre_cine = Column(String(100), nullable=False)
    direccion = Column(String(255), nullable=False)
    horarios_apertura = Column(String(100))
    url_mapa_embebido = Column(Text, default=None)
    estado_cine = Column(String(30), nullable=False, default="Activo")
    observaciones = Column(Text, default=None)
    eliminado = Column(Boolean, nullable=False, default=False)
    fecha_eliminacion = Column(DateTime, default=None)

    salas = relationship("Sala", back_populates="cine")
