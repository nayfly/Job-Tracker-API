from fastapi import FastAPI

from app.api.routers.applications import router as applications_router
from app.api.routers.auth import router as auth_router
from app.api.routers.companies import router as companies_router
from app.api.routers.followups import router as followups_router
from app.core.config import settings
from app.middleware.request_id import RequestIdMiddleware

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(RequestIdMiddleware)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(companies_router, prefix="/companies", tags=["companies"])
app.include_router(applications_router, prefix="/applications", tags=["applications"])
app.include_router(followups_router, prefix="/followups", tags=["followups"])
