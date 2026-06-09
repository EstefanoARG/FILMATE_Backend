from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class AsientoFuncion(Base):
    __tablename__ = "asientos_funciones"

    id_funcion = Column(Integer, ForeignKey("funciones.id_funcion", ondelete="CASCADE"), primary_key=True)
    id_asiento = Column(Integer, ForeignKey("asientos.id_asiento", ondelete="CASCADE"), primary_key=True)
    estado = Column(String(20), default="Disponible")

    funcion = relationship("Funcion", back_populates="asientos")
    asiento = relationship("Asiento", back_populates="funciones")
