from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

"""Modelo Rol.

Define roles de usuario y la relación inversa con `Usuario`.
"""

class Rol(Base):
    """Entidad `Rol`.
    """

    __tablename__ = "rol"

    id_rol = Column(Integer, primary_key=True)

    nombre = Column(
        String(50),
        unique=True,
        nullable=False
    )

    usuarios = relationship(
        "Usuario",
        back_populates="rol"
    )