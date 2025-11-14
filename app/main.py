"""FastAPI main application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.routes import classify, route
from app.utils.config import settings
from app.utils.logger import logger

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Loading AI models and services...")
    
    # Pre-load services
    try:
        from app.services.model_service import get_classifier
        classifier = get_classifier()
        logger.info("Classifier loaded successfully")
    except Exception as e:
        logger.warning(f"Could not pre-load classifier: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered support ticket triage and routing system",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(classify.router)
app.include_router(route.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "classify": "/classify",
            "route": "/route",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if services are available
        from app.services.model_service import get_classifier
        classifier = get_classifier()
        
        return {
            "status": "healthy",
            "services": {
                "classifier": "available",
                "model": classifier.model_name
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

