from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import verify_access_token

security_scheme = HTTPBearer(auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido",
        )
    payload = verify_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        )
    if not any(r in (1, 3) for r in payload.get("roles", [])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return payload


def get_current_superadmin(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    payload = verify_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")
    if 3 not in payload.get("roles", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requieren permisos de superadmin")
    return payload


def require_permiso(codigo_permiso: str):
    from app.repositories import permission_repository

    def checker(
        payload: dict = Depends(get_current_admin),
        db: Session = Depends(get_db),
    ):
        user_id = payload.get("user_id")
        if not permission_repository.user_has_permission(db, user_id, codigo_permiso):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso '{codigo_permiso}' requerido",
            )
        return payload
    return checker


def require_cualquier_permiso(codigos: list[str]):
    from app.repositories import permission_repository

    def checker(
        payload: dict = Depends(get_current_admin),
        db: Session = Depends(get_db),
    ):
        user_id = payload.get("user_id")
        for codigo in codigos:
            if permission_repository.user_has_permission(db, user_id, codigo):
                return payload
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Se requiere uno de estos permisos: {', '.join(codigos)}",
        )
    return checker