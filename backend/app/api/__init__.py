from app.api.auth import router as auth_router
from app.api.challenges import router as challenges_router
from app.api.institutions import router as institutions_router
from app.api.translate import router as translate_router

__all__ = [
    "auth_router",
    "challenges_router",
    "institutions_router",
    "translate_router",
]
