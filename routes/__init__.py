from fastapi import APIRouter
from routes.users import router as users_router
from routes.plans import router as plans_router

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(plans_router, prefix='/plans', tags=["Plans"])