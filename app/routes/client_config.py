from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.configuracion_sistema import ConfiguracionSistema

router = APIRouter(prefix="/client/configuracion", tags=["client config"])


@router.get("/sistema")
def get_system_config(db: Annotated[Session, Depends(get_db)]):
    items = (
        db.query(ConfiguracionSistema)
        .filter(ConfiguracionSistema.activo == True)  # noqa: E712
        .order_by(ConfiguracionSistema.clave.asc())
        .all()
    )

    return {
        "configuracion": [
            {
                "clave": item.clave,
                "valor": item.valor,
                "tipo_dato": item.tipo_dato,
                "categoria": item.categoria,
            }
            for item in items
        ]
    }
