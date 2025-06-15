import logging
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from pathlib import Path

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.security import get_current_active_user
from app.db.init_db import create_tables, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files directory if it exists
static_dir = Path("static")
if static_dir.exists():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(current_user=Depends(get_current_active_user)):
    """Custom Swagger UI that requires authentication"""
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - API Documentation",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint(current_user=Depends(get_current_active_user)):
    """Custom OpenAPI endpoint that requires authentication"""
    return get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Eira Clinical Notes and Reporting API",
        routes=app.routes,
    )


@app.get("/", include_in_schema=False)
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": f"Welcome to {settings.PROJECT_NAME} API"}


@app.get("/health", include_in_schema=False)
async def health_check():
    """Health check endpoint for monitoring systems"""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Creating database tables if they don't exist...")
    await create_tables()
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)