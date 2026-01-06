from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", response_class=JSONResponse)
async def health():
    """Health check endpoint."""
    return JSONResponse(status_code=200, content={"status": "ok"})
