from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base

class Rol(Base):
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