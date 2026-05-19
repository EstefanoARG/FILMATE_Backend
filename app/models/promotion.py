# backend/app/models/promotion.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    DateTime
)

from sqlalchemy.orm import relationship

from app.core.database import Base


class Promocion(Base):
    __tablename__ = "promocion"

    id_promocion = Column(
        Integer,
        primary_key=True
    )

    codigo_cupon = Column(
        String(20),
        unique=True,
        nullable=False
    )

    porcentaje_descuento = Column(
        DECIMAL(5, 2)
    )

    monto_descuento = Column(
        DECIMAL(8, 2)
    )

    fecha_inicio = Column(DateTime)

    fecha_fin = Column(DateTime)

    limite_usos = Column(Integer)

    reservas = relationship(
        "Reserva",
        back_populates="promocion"
    )