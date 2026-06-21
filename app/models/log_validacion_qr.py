from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, text
from app.core.database import Base


class LogValidacionQr(Base):
    __tablename__ = "log_validaciones_qr"

    id_log = Column(Integer, primary_key=True, autoincrement=True)
    ticket_escaneado = Column(String(100), nullable=False)
    fecha_escaneo = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    resultado_validacion = Column(String(20), nullable=False)
    id_usuario_control = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="SET NULL"), default=None)
