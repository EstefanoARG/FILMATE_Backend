from sqlalchemy import Column, Integer, String, Boolean, DateTime, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    id_tipo_doc = Column(Integer, ForeignKey("tipos_documento.id_tipo_doc"), nullable=False, default=1)
    numero_documento = Column(String(20), nullable=False)
    telefono = Column(String(20), default=None)
    url_perfil = Column(String(255), default="https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_1")
    estado_usuario = Column(String(20), nullable=False, default="ACTIVO")
    fecha_registro = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    ultima_conexion = Column(TIMESTAMP, default=None)
    eliminado = Column(Boolean, nullable=False, default=False)
    fecha_eliminacion = Column(DateTime, default=None)

    tipo_documento = relationship("TipoDocumento")
    roles = relationship("UsuarioRol", back_populates="usuario")
    resenas = relationship("Resena", back_populates="usuario")
    interacciones = relationship("InteraccionPelicula", back_populates="usuario")
    colecciones = relationship("Coleccion", back_populates="usuario")
