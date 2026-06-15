import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.dependencies import get_db
from app.models.historial_actividad import HistorialActividad
from app.schemas.historial_actividad import HistorialActividadResponse

# Importaciones necesarias para el summary
from app.models.user import Usuario
from app.models.review import Resena
from app.models.movie import Pelicula
from app.models.interaccion_pelicula import InteraccionPelicula

# Intentamos importar Seguidor (ajusta el nombre si en tu proyecto se llama distinto, ej. 'seguidores')
try:
    from app.models.seguidor import Seguidor
except ImportError:
    Seguidor = None

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/client/actividad", tags=["client actividad"])

# Schema para recibir la bio
class ProfileUpdate(BaseModel):
    bio: str

@router.get("/feed", response_model=List[HistorialActividadResponse])
def get_feed(db: Session = Depends(get_db)):
    return db.query(HistorialActividad).order_by(HistorialActividad.fecha_evento.desc()).limit(50).all()

@router.get("/usuario/{user_id}", response_model=List[HistorialActividadResponse])
def get_user_activity(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(HistorialActividad)
        .filter(HistorialActividad.id_usuario == user_id)
        .order_by(HistorialActividad.fecha_evento.desc())
        .limit(50)
        .all()
    )

@router.put("/profile/{user_id}")
def update_profile(user_id: int, payload: ProfileUpdate, db: Session = Depends(get_db)):
    """Actualiza la bio guardándola como un evento en el historial de actividad."""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    nueva_bio = HistorialActividad(
        id_usuario=user_id,
        tipo_evento='UPDATE_BIO',
        texto_breve=payload.bio
    )
    db.add(nueva_bio)
    db.commit()
    return {"message": "Perfil actualizado", "bio": payload.bio}

@router.get("/summary/{user_id}")
def get_social_summary(user_id: int, db: Session = Depends(get_db)):
    """Devuelve perfil (con la bio extraída), estadísticas y Top 5 ordenado."""
    usuario = db.query(Usuario).filter(Usuario.id_usuario == user_id, Usuario.eliminado == False).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Extraemos la bio desde el historial
    ultimo_evento_bio = (
        db.query(HistorialActividad)
        .filter(HistorialActividad.id_usuario == user_id, HistorialActividad.tipo_evento == 'UPDATE_BIO')
        .order_by(HistorialActividad.fecha_evento.desc())
        .first()
    )
    
    # Calculamos stats
    total_resenas = db.query(Resena).filter(Resena.id_usuario == user_id).count()
    seguidores_count = 0
    siguiendo_count = 0
    
    if Seguidor:
        seguidores_count = db.query(Seguidor).filter(Seguidor.id_seguido == user_id).count()
        siguiendo_count = db.query(Seguidor).filter(Seguidor.id_seguidor == user_id).count()
    
    # Extraemos el Top 5 respetando el orden artificial de fechas
    top_movies = (
        db.query(Pelicula)
        .join(InteraccionPelicula, Pelicula.id_pelicula == InteraccionPelicula.id_pelicula)
        .filter(InteraccionPelicula.id_usuario == user_id, InteraccionPelicula.favorita == True)
        .order_by(InteraccionPelicula.fecha_favorito.desc())
        .limit(5)
        .all()
    )
    
    return {
        "usuario": {
            "id": usuario.id_usuario,
            "username": usuario.username,
            "nombre": usuario.nombre,
            "bio": ultimo_evento_bio.texto_breve if ultimo_evento_bio else "",
            "url_perfil": usuario.url_perfil
        },
        "stats": {
            "total_reviews": total_resenas,
            "followers": seguidores_count,
            "following": siguiendo_count
        },
        "top_favorites": [
            {
                "id_pelicula": p.id_pelicula, 
                "titulo": p.titulo, 
                "url_poster": p.url_poster
            } for p in top_movies
        ]
    }