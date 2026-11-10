from fastapi import APIRouter, HTTPException, status

from sqlmodel import select

from api.schemas import *
from api.services import *

import re

router = APIRouter()

@router.put('/users/create', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def user_create(user_create: UserCreate, session: db_service.SessionDependency):
    user_create = UserCreate.model_validate(user_create)

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

@router.post('/users/update', response_model=UserResponse, status_code=status.HTTP_200_OK)
def user_update(user_update: UserUpdate, session: db_service.SessionDependency):
    user_update = UserUpdate.model_validate(user_update)

    user = auth_service.get_user_from_credentials(user_update, session)
    
    ...

    # postpone this feature


@router.delete('/users/delete', response_model=UserResponse, status_code=status.HTTP_200_OK)
def user_delete(user_login: UserLogin, session: db_service.SessionDependency):
    user_login = UserLogin.model_validate(user_login)

    user = auth_service.get_user_from_credentials(user_login, session)

    session.delete(user)
    session.commit()

    return {
        'detail': 'User successfully deleted',
        'data': user
    }
