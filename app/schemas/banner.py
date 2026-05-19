# backend/app/schemas/banner.py

from pydantic import BaseModel


class BannerBase(BaseModel):
    id_pelicula: int
    imagen_url: str
    orden: int


class BannerCreate(BannerBase):
    pass


class BannerResponse(BannerBase):
    id_banner: int
    is_activo: bool

    class Config:
        from_attributes = True