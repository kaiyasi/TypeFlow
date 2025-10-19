import sys
import os
sys.path.append('/app')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Configure basic logging
logger = structlog.get_logger()

# Create FastAPI app
app = FastAPI(
    title="TypeFlow API",
    description="Advanced Multi-Language Typing Practice Platform",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://typeflow.serelix.xyz",
        "http://localhost:12012",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TypeFlow API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "typeflow-api"}

@app.get("/api/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "TypeFlow API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/healthz",
            "docs": "/docs",
            "api_root": "/api/"
        }
    }

@app.get("/api/auth/me")
async def get_current_user():
    """Get current user - placeholder"""
    return {"user": None, "authenticated": False}

@app.on_event("startup")
async def startup_event():
    logger.info("TypeFlow API started successfully")

@app.on_event("shutdown")  
async def shutdown_event():
    logger.info("TypeFlow API shut down complete")