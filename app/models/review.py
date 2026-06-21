from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Resena(Base):
    __tablename__ = "resenas"

    id_resena = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    id_pelicula = Column(Integer, ForeignKey("peliculas.id_pelicula", ondelete="CASCADE"))
    puntuacion_estrellas = Column(Integer, default=None)
    comentario = Column(Text)
    fecha_publicacion = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    usuario = relationship("Usuario", back_populates="resenas")
    pelicula = relationship("Pelicula", back_populates="resenas")
