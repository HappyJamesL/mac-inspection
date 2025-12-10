"""权限验证工具"""
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.core.config import settings
from app.api.routes.auth import oauth2_scheme


async def verify_role(token: str = Depends(oauth2_scheme)) -> bool:
    """验证角色是否为配置的角色"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        role: str = payload.get("role")
        if role is None or role != settings.ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
    except JWTError:
        raise credentials_exception
