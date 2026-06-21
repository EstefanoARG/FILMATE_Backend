from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Coleccion(Base):
    __tablename__ = "colecciones"

    id_coleccion = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    titulo_coleccion = Column(String(150), nullable=False)
    descripcion = Column(Text)
    fecha_creacion = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    eliminado = Column(Boolean, nullable=False, default=False)
    fecha_eliminacion = Column(DateTime, default=None)

    usuario = relationship("Usuario", back_populates="colecciones")
    peliculas = relationship("ColeccionPelicula", back_populates="coleccion")
