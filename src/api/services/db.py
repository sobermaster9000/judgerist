from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

sqliteFilename = 'database.db'
sqliteUrl = f'sqlite:///{sqliteFilename}'

engine = create_engine(sqliteUrl, connect_args={ 'check_same_thread': False })

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDependency = Annotated[Session, Depends(get_session)]

# TODO: add logger
