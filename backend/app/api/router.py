from fastapi import APIRouter

from app.api.routes import admin, auth, generators, modes, progress

api_router = APIRouter()
api_router.include_router(auth.router, prefix='/auth', tags=['Auth'])
api_router.include_router(generators.router, prefix='/generators', tags=['Generatorer'])
api_router.include_router(modes.router, prefix='/modes', tags=['Moduser'])
api_router.include_router(progress.router, prefix='/progress', tags=['Progresjon'])
api_router.include_router(admin.router, prefix='/admin', tags=['Admin'])
