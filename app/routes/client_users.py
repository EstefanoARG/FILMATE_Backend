import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.cinema import Cine
from app.models.detalle_boleta_asiento import DetalleBoletaAsiento
from app.models.detalle_boleta_confiteria import DetalleBoletaConfiteria
from app.models.boleta_ticket import BoletaTicket
from app.models.historial_actividad import HistorialActividad
from app.models.interaccion_pelicula import InteraccionPelicula
from app.models.movie import Pelicula
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.snack_product import ProductoConfiteria
from app.models.transaccion import Transaccion
from app.schemas.movie import MovieResponse, FavoriteMovieResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/users", tags=["client users"])

TOP_FAVORITO_EVENT = "TOP_FAVORITO"


class TopFavoritesUpdate(BaseModel):
    movie_ids: List[int]


@router.get("/{user_id}/favorite-movies", response_model=List[FavoriteMovieResponse])
def get_favorite_movies(user_id: int, db: Annotated[Session, Depends(get_db)], genero_id: Optional[int] = None):
    """Retorna la lista completa de películas marcadas como favoritas por un usuario, con la fecha en que se marcó cada una."""
    query = (
        db.query(Pelicula, InteraccionPelicula.fecha_favorito)
        .join(InteraccionPelicula, Pelicula.id_pelicula == InteraccionPelicula.id_pelicula)
        .filter(
            InteraccionPelicula.id_usuario == user_id,
            InteraccionPelicula.favorita == True,
            Pelicula.eliminado == False,
        )
    )
    if genero_id is not None:
        query = query.filter(Pelicula.generos.any(id_genero=genero_id))

    rows = query.order_by(InteraccionPelicula.fecha_favorito.desc()).all()
    return [
        FavoriteMovieResponse(**MovieResponse.model_validate(pelicula).model_dump(), fecha_favorito=fecha_favorito)
        for pelicula, fecha_favorito in rows
    ]


@router.get("/{user_id}/favorite-movies/count")
def get_favorite_movies_count(user_id: int, db: Annotated[Session, Depends(get_db)]):
    total = (
        db.query(InteraccionPelicula)
        .filter(InteraccionPelicula.id_usuario == user_id, InteraccionPelicula.favorita == True)
        .count()
    )
    return {"total_favoritos": total}


@router.put(
    "/{user_id}/favorite-movies",
    responses={400: {"description": "Máximo 5 películas permitidas, o alguna no está en tus favoritas"}},
)
def update_top_favorites(user_id: int, payload: TopFavoritesUpdate, db: Annotated[Session, Depends(get_db)]):
    """Guarda las 5 películas destacadas del perfil, separado de la lista completa de favoritas.

    Las destacadas viven como eventos en historial_actividad (tipo_evento=TOP_FAVORITO) en vez de
    reutilizar InteraccionPelicula.favorita, porque ese campo representa la lista completa de
    favoritas y no debe alterarse al elegir las destacadas (ni viceversa).
    """
    if len(payload.movie_ids) > 5:
        raise HTTPException(status_code=400, detail="Máximo 5 películas permitidas")

    favorited_ids = {
        row[0]
        for row in db.query(InteraccionPelicula.id_pelicula)
        .filter(InteraccionPelicula.id_usuario == user_id, InteraccionPelicula.favorita == True)
        .all()
    }
    invalid_ids = [movie_id for movie_id in payload.movie_ids if movie_id not in favorited_ids]
    if invalid_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Las películas {invalid_ids} no están en tu lista de favoritas",
        )

    db.query(HistorialActividad).filter(
        HistorialActividad.id_usuario == user_id,
        HistorialActividad.tipo_evento == TOP_FAVORITO_EVENT,
    ).delete()

    for movie_id in payload.movie_ids:
        db.add(
            HistorialActividad(
                id_usuario=user_id,
                tipo_evento=TOP_FAVORITO_EVENT,
                id_referencia_pelicula=movie_id,
                texto_breve="Destacó esta película en su perfil",
            )
        )

    db.commit()
    return {"message": "Top 5 actualizado y ordenado correctamente"}


def _serialize_purchase(db: Session, transaccion: Transaccion, funcion: Optional[Funcion], pelicula: Optional[Pelicula], sala: Optional[Sala], cine: Optional[Cine]) -> dict:
    detalle_asientos = db.query(DetalleBoletaAsiento).filter(DetalleBoletaAsiento.id_transaccion == transaccion.id_transaccion).all()
    seat_ids = [d.id_asiento for d in detalle_asientos]
    seats_by_id = {s.id_asiento: s for s in db.query(Asiento).filter(Asiento.id_asiento.in_(seat_ids)).all()} if seat_ids else {}

    detalle_confiteria = db.query(DetalleBoletaConfiteria).filter(DetalleBoletaConfiteria.id_transaccion == transaccion.id_transaccion).all()
    producto_ids = [d.id_producto for d in detalle_confiteria]
    productos_by_id = {p.id_producto: p for p in db.query(ProductoConfiteria).filter(ProductoConfiteria.id_producto.in_(producto_ids)).all()} if producto_ids else {}

    tickets = db.query(BoletaTicket).filter(BoletaTicket.id_transaccion == transaccion.id_transaccion).all()

    return {
        "id_transaccion": transaccion.id_transaccion,
        "fecha": transaccion.fecha_transaccion,
        "monto_total": float(transaccion.monto_total),
        "metodo_pago": transaccion.metodo_pago,
        "estado_pago": transaccion.estado_pago,
        "pelicula": {
            "id_pelicula": pelicula.id_pelicula,
            "titulo": pelicula.titulo,
            "url_poster": pelicula.url_poster,
        } if pelicula else None,
        "sede": {"id_cine": cine.id_cine, "nombre_cine": cine.nombre_cine} if cine else None,
        "sala": {"id_sala": sala.id_sala, "nombre_sala": sala.nombre_sala} if sala else None,
        "fecha_hora_funcion": funcion.fecha_hora if funcion else None,
        "pdf_url": f"/client/tickets/transaction/{transaccion.id_transaccion}/pdf",
        "asientos": [
            {
                "id_asiento": d.id_asiento,
                "fila": seats_by_id[d.id_asiento].fila if d.id_asiento in seats_by_id else None,
                "columna": seats_by_id[d.id_asiento].columna if d.id_asiento in seats_by_id else None,
            }
            for d in detalle_asientos
        ],
        "productos_confiteria": [
            {
                "id_producto": d.id_producto,
                "nombre_producto": productos_by_id[d.id_producto].nombre_producto if d.id_producto in productos_by_id else None,
                "cantidad": d.cantidad,
                "precio_unitario": float(d.precio_unitario),
            }
            for d in detalle_confiteria
        ],
        "tickets": [
            {"id_ticket": t.id_ticket, "codigo_qr_token": t.codigo_qr_token, "estado_ticket": t.estado_ticket}
            for t in tickets
        ],
    }


@router.get("/{user_id}/purchases")
def get_user_purchases(user_id: int, db: Annotated[Session, Depends(get_db)], limit: Optional[int] = None):
    """Historial de compras del usuario (entradas, dulcería, o ambas)."""
    query = (
        db.query(Transaccion, Funcion, Pelicula, Sala, Cine)
        .outerjoin(Funcion, Transaccion.id_funcion == Funcion.id_funcion)
        .outerjoin(Pelicula, Funcion.id_pelicula == Pelicula.id_pelicula)
        .outerjoin(Sala, Funcion.id_sala == Sala.id_sala)
        .outerjoin(Cine, Sala.id_cine == Cine.id_cine)
        .filter(Transaccion.id_usuario == user_id)
        .order_by(Transaccion.fecha_transaccion.desc())
    )
    if limit is not None:
        query = query.limit(limit)

    rows = query.all()
    return [_serialize_purchase(db, transaccion, funcion, pelicula, sala, cine) for transaccion, funcion, pelicula, sala, cine in rows]
