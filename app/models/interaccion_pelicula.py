from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class InteraccionPelicula(Base):
    __tablename__ = "interacciones_peliculas"

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_pelicula = Column(Integer, ForeignKey("peliculas.id_pelicula", ondelete="CASCADE"), primary_key=True)
    vista = Column(Boolean, default=False)
    favorita = Column(Boolean, default=False)
    en_lista_seguimiento = Column(Boolean, default=False)
    fecha_favorito = Column(TIMESTAMP, default=None)

    usuario = relationship("Usuario", back_populates="interacciones")
