"""DecisionOS Backend Application Main Entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints.health import get_health, HealthResponse
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan context manager."""
    logger.info("Initializing DecisionOS Backend API...")
    logger.info(f"Environment: {settings.ENVIRONMENT} | Version: {settings.VERSION}")
    yield
    logger.info("Shutting down DecisionOS Backend API...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Top-level Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Top-level health endpoint."""
    return get_health()


# Top-level Root endpoint
@app.get("/", tags=["Root"])
def root():
    """Root status endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "health_check": "/health",
        "api_v1": settings.API_V1_STR,
    }
