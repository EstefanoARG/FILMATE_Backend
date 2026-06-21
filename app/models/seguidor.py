from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, text
from app.core.database import Base


class Seguidor(Base):
    __tablename__ = "seguidores"

    id_seguidor = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_seguido = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    fecha_seguimiento = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
