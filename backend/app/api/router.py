from fastapi import APIRouter

from app.api.routes import generators, modes

api_router = APIRouter()
api_router.include_router(generators.router, prefix='/generators', tags=['Generatorer'])
api_router.include_router(modes.router, prefix='/modes', tags=['Moduser'])
