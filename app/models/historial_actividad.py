from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from app.core.database import Base


class HistorialActividad(Base):
    __tablename__ = "historial_actividad"

    id_actividad = Column(Integer, primary_key=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    tipo_evento = Column(String(20), nullable=False)
    id_referencia_usuario = Column(Integer, default=None)
    id_referencia_pelicula = Column(Integer, default=None)
    id_referencia_resena = Column(Integer, default=None)
    texto_breve = Column(Text)
    fecha_evento = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
