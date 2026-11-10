import os
import hashlib, secrets
from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from sqlmodel import select
import jwt

from api.schemas import *
from api.config import settings
from .db import SessionDependency

TOKEN_SECURITY = HTTPBearer()

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    iterations = settings.HASHING_ITERATIONS
    hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    return f"{iterations}:{salt.hex()}:{hash.hex()}"

def is_password_match(password_hash: str, password: str) -> bool:
    iterations, salt, hash = password_hash.split(':')
    iterations = int(iterations)
    salt, hash = bytes.fromhex(salt), bytes.fromhex(hash)

    new_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    
    return secrets.compare_digest(hash, new_hash)

def get_user_from_credentials(user_login: UserLogin, session: SessionDependency) -> User:
    user = session.exec(select(User).where(User.email == user_login.email)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Email not associated with any user')

    if user_login.username and user_login.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username')
    
    if not is_password_match(user.password_hash, user_login.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    return user

def get_token_from_credentials(user_login: UserLogin, session: SessionDependency) -> str:
    user = session.exec(select(User).where(User.email == user_login.email)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Email not associated with any user')

    if user_login.username and user_login.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username')
    
    if not is_password_match(user.password_hash, user_login.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    payload = {
        'email': user.email,
        'created_at': datetime.now(timezone.utc).timestamp()
    }

    token = jwt.encode(payload, settings.JWT_SIGNATURE, algorithm='HS256')

    return token

def get_user_from_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(TOKEN_SECURITY)], session: SessionDependency) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, settings.JWT_SIGNATURE, algorithms=['HS256']) # replace with proper secret
    email, created_at = payload.get('email'), payload.get('created_at')

    if not email or not created_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    if datetime.now(timezone.utc) >= datetime.fromtimestamp(created_at) + timedelta(hours=settings.TOKEN_EXPIRY_HOURS):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid')

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Email not associated with any user')

    if user.reject_tokens_before and datetime.fromtimestamp(created_at) <= user.reject_tokens_before:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token is invalid')

    return user

def update_token_rejection_timestamp(user: User, session: SessionDependency) -> None:
    user.reject_tokens_before = datetime.now(timezone.utc)

    session.add(user)
    session.commit()
    session.refresh(user)
