from pydantic import BaseModel
from app.schemas.user import UserResponse


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
