from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserResponse


class LoginResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
