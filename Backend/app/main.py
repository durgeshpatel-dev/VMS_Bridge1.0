from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import get_settings


settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.version)

# Include API routers
from app.api.routes.health import router as health_router

app.include_router(health_router)


@app.get("/health")
async def health():
    return JSONResponse(status_code=200, content={"status": "ok"})


# Optionally, include more routers here in the future
