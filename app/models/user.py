from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

"""Modelo Usuario.

Representa a un usuario del sistema con información básica, rol y
relaciones con reservas, favoritos y reseñas.
"""

class Usuario(Base):
    """Entidad `Usuario`.

    Atributos clave:
    - `id_usuario`: identificador del usuario.
    - `correo`: email único usado para login.
    - `rol`: relación con `Rol`.
    """
    __tablename__ = "usuario"

    id_usuario = Column(
        Integer,
        primary_key=True,
        index=True
    )

    id_rol = Column(
        Integer,
        ForeignKey("rol.id_rol"),
        nullable=False
    )

    nombres = Column(
        String(100),
        nullable=False
    )

    apellidos = Column(
        String(100),
        nullable=False
    )

    correo = Column(
        String(150),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    estado = Column(
        Enum(
            "Activo",
            "Bloqueado",
            "Inactivo",
            name="estado_usuario"
        ),
        default="Activo"
    )

    fecha_registro = Column(
        DateTime,
        server_default=func.now()
    )

    rol = relationship(
        "Rol",
        back_populates="usuarios"
    )

    favoritos = relationship(
        "Favorito",
        back_populates="usuario"
    )

    reservas = relationship(
        "Reserva",
        back_populates="usuario"
    )

    resenas = relationship(
        "Resena",
        back_populates="usuario"
    )