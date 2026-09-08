from fastapi import FastAPI

from app.api import auth_router, challenges_router, institutions_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

app.include_router(auth_router)
app.include_router(challenges_router)
app.include_router(institutions_router)


@app.get("/health", tags=["Health"])
def get_health():
    return {
        "status": "healthy",
        "service": "SolveSphere API",
    }

