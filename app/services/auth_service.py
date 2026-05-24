from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.users import UserModel
from app.core.security import create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.utils.id_generator import generate_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

class AuthService:

    def __init__(self, db: Session):
        self._db = db

    def register(self, payload: RegisterRequest) -> TokenResponse:

        if self._db.query(UserModel).filter(UserModel.email == payload.email).first():
            raise HTTPException(
                status_code= status.HTTP_409_CONFLICT,
                detail= "An Account with the email already exists"
            )
        
        if self._db.query(UserModel).filter(UserModel.username == payload.username).first():
            raise HTTPException(
                status_code= status.HTTP_409_CONFLICT,
                detail= "This username is already taken"
            )
        
        user = UserModel(
            id = generate_id(),
            email = payload.email.lower().strip(),
            username= payload.username.strip(),
            password= payload.password(payload.password)
        )

        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)

        token = create_access_token(user.id)

        return TokenResponse(
            access_token= token,
            user= UserOut(**user.to_dict())
        )
    
    def login(self, payload: LoginRequest) -> TokenResponse:

        user = self._db.query(UserModel).filter(UserModel.email == payload.email).first()

        auth_error = HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Username or Password incorrect"
        )

        if not user:
            raise auth_error
        
        if not verify_password(payload.password, user.password):
            raise auth_error
        
        if not user.is_active:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail= "Account is disabled."
            )
        
        token = create_access_token(user.id)
        return TokenResponse(
            access_token= token,
            user= UserOut(**user.to_dict())
        )