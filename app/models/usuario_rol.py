from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class UsuarioRol(Base):
    __tablename__ = "usuarios_roles"

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_role = Column(Integer, ForeignKey("roles.id_role", ondelete="CASCADE"), primary_key=True)

    usuario = relationship("Usuario", back_populates="roles")
