from pydantic import BaseModel, EmailStr

from sqlmodel import SQLModel, Field

from datetime import datetime, timezone

class UserBase(SQLModel):
    username: str = Field(max_length=64)
    email: EmailStr = Field(max_length=64, unique=True, index=True)

    created_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc),
                                        sa_column_kwargs={ 'onupdate': lambda: datetime.now(timezone.utc) })

class User(UserBase, table=True):
    __tablename__: str = 'users'

    id: int | None = Field(default=None, primary_key=True)
    password_hash: str

class UserPublic(UserBase):
    id: int

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str

class UserLogin(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserUpdate(UserLogin):
    username_new: str | None
    email_new: EmailStr | None
    password_new: str | None
    password_new_confirm: str | None

class UserTokenRequest(UserLogin):
    req_tok_expiry_mins: int | None
    req_tok_expiry_hours: int | None
    req_tok_expiry_days: int | None

class UserTokenDeleteRequest(UserLogin):
    active_token: str | None

class UserResponse(BaseModel):
    detail: str
    data: UserPublic

class UserListResponse(BaseModel):
    detail: str
    data: list[UserPublic]

class UserTokenResponse(BaseModel):
    detail: str
    data: str
