from fastapi import APIRouter

from app.api.v1 import audit, auth, documents, qa, subscriptions

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(subscriptions.router)
api_router.include_router(documents.router)
api_router.include_router(audit.router)
api_router.include_router(qa.router)
