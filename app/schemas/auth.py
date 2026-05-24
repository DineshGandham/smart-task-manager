from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# ── Request schemas ────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length= 3, max_length= 50, pattern= r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length= 100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ── Response schemas ───────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    users: UserOut