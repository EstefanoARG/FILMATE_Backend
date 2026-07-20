from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, text
from app.core.database import Base


class NotificacionLeida(Base):
    __tablename__ = "notificaciones_leidas"

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_actividad = Column(Integer, ForeignKey("historial_actividad.id_actividad", ondelete="CASCADE"), primary_key=True)
    fecha_lectura = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
