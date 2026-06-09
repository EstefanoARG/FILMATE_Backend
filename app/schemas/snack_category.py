from pydantic import BaseModel


class SnackCategoryBase(BaseModel):
    nombre_categoria: str


class SnackCategoryCreate(SnackCategoryBase):
    pass


class SnackCategoryResponse(SnackCategoryBase):
    id_categoria_confi: int

    model_config = {"from_attributes": True}
