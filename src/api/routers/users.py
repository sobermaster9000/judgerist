from fastapi import APIRouter, HTTPException, status

from sqlmodel import select

from api.schemas import User, UserResponse, UserCreate
from api.services import auth_service, db_service

import re

router = APIRouter()

@router.put('/users/create', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def user_create(user_create: UserCreate, session: db_service.SessionDependency):
    user_create = user_create.model_validate(user_create)
    
    user_duplicate = session.exec(select(User).where(User.email == str(user_create.email))).first()
    if user_duplicate:
        raise HTTPException(status_code=422, detail='Email elready exists')

    if user_create.password != user_create.password_confirm:
        raise HTTPException(status_code=422, detail='Passwords do not match')

    isValidPassword = re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[^A-Za-z\\d]).{8,}$", user_create.password)
    if not isValidPassword:
        raise HTTPException(status_code=422, detail="Password must be at least 8 characters long and have at least one of all the following: lowercase letter, uppercase letter, number, special character")

    passwordHash = auth_service.hash_password(user_create.password)

    user = User(
        username=user_create.username,
        email=user_create.email,
        password_hash=passwordHash,
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return {
        "detail": "User successfully created",
        "data": user
    }

@router.post('/users/get-token')
def user_login():
    pass

@router.post('/users/invalidate-token')
def user_logout():
    pass

@router.delete('/users/delete')
def user_delete():
    pass
