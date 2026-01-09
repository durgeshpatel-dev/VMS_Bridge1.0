from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings


settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.version)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite
        "http://localhost:3000",  # React/Node dev server
        "http://localhost:4173",  # Vite preview
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.scans import router as scans_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.vulnerabilities import router as vulnerabilities_router

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(scans_router)
app.include_router(jobs_router)
app.include_router(vulnerabilities_router)


@app.get("/health")
async def health():
    return JSONResponse(status_code=200, content={"status": "ok"})


# Optionally, include more routers here in the future
