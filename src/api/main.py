from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

# specify which are imported in prod
from api.schemas import *
from api.routers import users_router, problems_router, submissions_router
from api.services import auth_service, db_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print('judgerist startup')
    # do something with db

    yield

    # shutdown
    print('judgerist shutdown')

app = FastAPI(
    title='judgerist',
    description='A simple code judge API.',
    version='1.0',
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,    # since allow_origins is *
    allow_methods=['*'],
    allow_headers=['*']
)

# add auth stuff

'''
API return object format:

success:
{
    message: '',
    result: {

    }
}

error:
{
    message: '',
    errors: {

    }
}
'''

# add db init / verification

app.include_router(users_router, tags=['users'])
app.include_router(problems_router, tags=['problems'])
app.include_router(submissions_router, tags=['submissions'])

@app.get('/')
def root():
    return { 'message': f'Hello from {app.title}!' }
