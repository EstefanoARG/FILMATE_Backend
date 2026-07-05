import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_admin
from app.models.configuracion_sistema import ConfiguracionSistema
from app.models.snack_product import ProductoConfiteria
from app.schemas.configuracion import (
    PreciosFormatoRequest, PreciosFormatoResponse,
    PreciosSalaFormatoRequest, PreciosSalaFormatoResponse,
    TiposEntradaRequest, TiposEntradaResponse,
    ConfiteriaListResponse, ConfiteriaProductoItem,
    ConfiteriaCreateRequest, ConfiteriaUpdateRequest,
    ParametrosListResponse, ParametroSistemaItem,
    ParametroUpdateRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/config", tags=["admin config"])


def _get_config_or_404(db: Session, clave: str) -> ConfiguracionSistema:
    cfg = db.query(ConfiguracionSistema).filter(
        ConfiguracionSistema.clave == clave
    ).first()
    if not cfg:
        raise HTTPException(status_code=404, detail=f"Configuración '{clave}' no encontrada")
    return cfg


@router.get("/precios-formato", response_model=PreciosFormatoResponse)
def get_precios_formato(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    cfg = _get_config_or_404(db, "precios_formato")
    raw = json.loads(cfg.valor)
    precios = [{"formato": k, "precio": v} for k, v in raw.items()]
    return {"precios": precios}


@router.put("/precios-formato", response_model=PreciosFormatoResponse)
def update_precios_formato(
    payload: PreciosFormatoRequest,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    cfg = _get_config_or_404(db, "precios_formato")
    obj = {p.formato: p.precio for p in payload.precios}
    cfg.valor = json.dumps(obj, ensure_ascii=False)
    db.commit()
    db.refresh(cfg)
    return {"precios": payload.precios}


@router.get("/precios-sala-formato", response_model=PreciosSalaFormatoResponse)
def get_precios_sala_formato(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    cfg = _get_config_or_404(db, "precios_sala_formato")
    precios = json.loads(cfg.valor)
    return {"precios": precios}


@router.put("/precios-sala-formato", response_model=PreciosSalaFormatoResponse)
def update_precios_sala_formato(
    payload: PreciosSalaFormatoRequest,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    cfg = _get_config_or_404(db, "precios_sala_formato")
    cfg.valor = json.dumps([p.model_dump() for p in payload.precios], ensure_ascii=False)
    db.commit()
    db.refresh(cfg)
    return {"precios": payload.precios}


@router.get("/tipos-entrada", response_model=TiposEntradaResponse)
def get_tipos_entrada(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    cfg = _get_config_or_404(db, "tipos_entrada")
    tipos = json.loads(cfg.valor)
    return {"tipos": tipos}


@router.put("/tipos-entrada", response_model=TiposEntradaResponse)
def update_tipos_entrada(
    payload: TiposEntradaRequest,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    cfg = _get_config_or_404(db, "tipos_entrada")
    cfg.valor = json.dumps([t.model_dump() for t in payload.tipos], ensure_ascii=False)
    db.commit()
    db.refresh(cfg)
    return {"tipos": payload.tipos}


@router.get("/confiteria", response_model=ConfiteriaListResponse)
def list_confiteria(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    productos = db.query(ProductoConfiteria).order_by(ProductoConfiteria.id_producto).all()
    items = [
        ConfiteriaProductoItem(id=p.id_producto, nombre=p.nombre_producto, precio=float(p.precio))
        for p in productos
    ]
    return {"productos": items}


@router.post("/confiteria", response_model=ConfiteriaProductoItem, status_code=201)
def create_confiteria(
    payload: ConfiteriaCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    producto = ProductoConfiteria(
        nombre_producto=payload.nombre,
        precio=payload.precio,
        id_categoria_confi=payload.id_categoria_confi,
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return ConfiteriaProductoItem(id=producto.id_producto, nombre=producto.nombre_producto, precio=float(producto.precio))


@router.put("/confiteria/{producto_id}", response_model=ConfiteriaProductoItem)
def update_confiteria(
    producto_id: int,
    payload: ConfiteriaUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    producto = db.query(ProductoConfiteria).filter(ProductoConfiteria.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if payload.nombre is not None:
        producto.nombre_producto = payload.nombre
    if payload.precio is not None:
        producto.precio = payload.precio
    db.commit()
    db.refresh(producto)
    return ConfiteriaProductoItem(id=producto.id_producto, nombre=producto.nombre_producto, precio=float(producto.precio))


@router.delete("/confiteria/{producto_id}")
def delete_confiteria(
    producto_id: int,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    producto = db.query(ProductoConfiteria).filter(ProductoConfiteria.id_producto == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return {"message": "Producto eliminado"}


@router.get("/params", response_model=ParametrosListResponse)
def list_params(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    registros = db.query(ConfiguracionSistema).filter(
        ConfiguracionSistema.activo == True
    ).order_by(ConfiguracionSistema.categoria, ConfiguracionSistema.id_config).all()
    items = [
        ParametroSistemaItem(
            clave=r.clave, valor=r.valor, descripcion=r.descripcion,
            tipo_dato=r.tipo_dato, categoria=r.categoria, activo=r.activo
        )
        for r in registros
    ]
    return {"params": items}


@router.put("/params/{clave}", response_model=ParametroSistemaItem)
def update_param(
    clave: str,
    payload: ParametroUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[dict, Depends(get_current_admin)],
):
    cfg = _get_config_or_404(db, clave)
    cfg.valor = payload.valor
    db.commit()
    db.refresh(cfg)
    return ParametroSistemaItem(
        clave=cfg.clave, valor=cfg.valor, descripcion=cfg.descripcion,
        tipo_dato=cfg.tipo_dato, categoria=cfg.categoria, activo=cfg.activo
    )
