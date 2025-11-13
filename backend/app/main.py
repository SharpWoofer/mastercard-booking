from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database.db import create_tables_with_feedback
from app.routers import bookings, auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Creates database tables on startup.
    """
    logger.info("Starting up application...")
    try:
        create_tables_with_feedback()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise
    
    yield
    
    logger.info("Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Meeting Room Booking API",
    description="API for managing meeting room bookings with user authentication and overlap detection",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(bookings.router)

@app.get("/", tags=["health"])
def read_root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Meeting Room Booking API is running",
        "version": "2.0.0"
    }

@app.get("/health", tags=["health"])
def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "api": "operational",
        "features": ["authentication", "authorization", "booking_management"]
    }