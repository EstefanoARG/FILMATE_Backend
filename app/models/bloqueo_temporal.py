from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from app.core.database import Base


class BloqueoTemporal(Base):
    __tablename__ = "bloqueos_temporales"

    id_bloqueo = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    id_funcion = Column(Integer, nullable=False)
    id_asiento = Column(Integer, nullable=False)
    fecha_bloqueo = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    expira_en = Column(TIMESTAMP, nullable=False)
