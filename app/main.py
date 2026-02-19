import logging
from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy import text
from starlette.requests import Request

from app.core.deps import get_db
from app.core import logging as logging_config

from app.api.routers.applications import router as applications_router
from app.api.routers.auth import router as auth_router
from app.api.routers.companies import router as companies_router
from app.api.routers.followups import router as followups_router
from app.core.config import settings
from app.middleware.request_id import RequestIdMiddleware

# configure logging as soon as app starts
logging_config.setup_logging(json_output=True)

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(RequestIdMiddleware)

# basic prometheus metrics
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter("app_requests_total", "Total requests", ["method", "endpoint", "http_status"])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    return response

@app.get("/metrics", tags=["system"])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)



@app.get("/health", tags=["system"])
def health(db=Depends(get_db)):
    # execute a cheap query to ensure the database is reachable
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable")
    # log something so we have a record to inspect
    logging.getLogger(__name__).info("health check passed")
    return {"status": "ok"}


app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(companies_router, prefix="/companies", tags=["companies"])
app.include_router(applications_router, prefix="/applications", tags=["applications"])
app.include_router(followups_router, prefix="/followups", tags=["followups"])
