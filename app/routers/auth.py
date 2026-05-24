from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.users import UserModel
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db=db)


@router.post("/register", response_model= TokenResponse, status_code= status.HTTP_201_CREATED)
def register(
        payload: RegisterRequest,
        service: AuthService = Depends(get_auth_service),
):
    

    return service.register(payload)

@router.post("/login", response_model= TokenResponse)
def login(
        payload: LoginRequest,
        service: AuthService = Depends(get_auth_service)
):
    return service.login(payload)


@router.get("/me", response_model= UserOut)
def me(current_user: UserModel = Depends(get_current_user)):
    
    """
    Get the currently authenticated user's profile.
    Requires Authorization: Bearer <token> header.
    """
    return UserOut(**current_user.to_dict())