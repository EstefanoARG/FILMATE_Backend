from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from app.core.database import Base


class LogActividadSistema(Base):
    __tablename__ = "log_actividad_sistema"

    id_log = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="SET NULL"))
    accion_realizada = Column(Text, nullable=False)
    modulo_afectado = Column(String(50), nullable=False)
    ip_origen = Column(String(45), nullable=False)
    fecha_hora = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
