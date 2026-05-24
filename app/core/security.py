from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.users import UserModel

settings = get_settings()

# HTTPBearer reads the Authorization: Bearer <token> header automatically
bearer_scheme = HTTPBearer()


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        hours= settings.ACCESS_TOKEN_EXPIRE_HOURS
    )

    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc) 
    }

    return jwt.encode(payload, settings.SECRETE_KEY, settings.JWT_ALGORITHM)

def decode_token(token: str) -> Optional[str]:

    try:
        payload = jwt.decode(
            token,
            settings.SECRETE_KEY,
            algorithms= [settings.JWT_ALGORITHM],
        )
        return payload.get("sub")
    except JWTError:
        return None

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db)
) -> UserModel:

    credentials_exception = HTTPException(
        status_code= status.HTTP_401_UNAUTHORIZED,
        detail= "Invalid or expired token. Please log in again.",
        headers= {"WWW-Authenticate" : "Bearer"},
    )

    user_id = decode_token(credentials.credentials)
    if not user_id:
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= "Account is disabled. "
        )
    
    return user