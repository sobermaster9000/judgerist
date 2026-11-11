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

def get_token_from_credentials(user_token_request: UserTokenRequest, session: SessionDependency) -> str:
    user = session.exec(select(User).where(User.email == user_token_request.email)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not associated with any user')

    if user_token_request.username and user_token_request.username != user.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect username')
    
    if not is_password_match(user.password_hash, user_token_request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    req_mins = user_token_request.req_tok_expiry_mins
    req_hours = user_token_request.req_tok_expiry_hours
    req_days = user_token_request.req_tok_expiry_days

    payload = { 'email': user.email }

    if not any([req_mins, req_hours, req_days]):
        payload['expires_on'] = {
            (datetime.now(timezone.utc) + timedelta(hours=settings.TOKEN_EXPIRY_HOURS)).timestamp()
        }
    else:
        payload['expires_on'] = (datetime.now(timezone.utc) + timedelta(
            minutes=(req_mins if req_mins else 0),
            hours=(req_hours if req_hours else 0),
            days=(req_days if req_days else 0)
        )).timestamp()

    payload = {
        'email': user.email,
        'expires_on': (datetime.now(timezone.utc) + timedelta(
            minutes=(req_mins if req_mins else 0),
            hours=(req_hours if req_hours else 0),
            days=(req_days if req_days else 0))).timestamp(),
    }

    token = jwt.encode(payload, settings.JWT_SIGNATURE, algorithm='HS256')

    return token

def get_user_from_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(TOKEN_SECURITY)], session: SessionDependency) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, settings.JWT_SIGNATURE, algorithms=['HS256'])
    email, expires_at = payload.get('email'), payload.get('expires_at')

    if not email or not expires_at:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    if datetime.now(timezone.utc) >= datetime.fromtimestamp(expires_at):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid')

    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not associated with any user')

    return user
