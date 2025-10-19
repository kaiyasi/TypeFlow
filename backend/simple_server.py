#!/usr/bin/env python3
"""
Simple working server for TypeFlow
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="TypeFlow API",
    description="TypeFlow Backend API", 
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "TypeFlow API", "status": "running"}

@app.get("/healthz")
def health():
    return {"status": "healthy"}

@app.get("/api/")
def api_root():
    return {"api": "TypeFlow API v1.0.0"}

@app.get("/api/auth/me")
def auth_me():
    return {"user": None, "authenticated": False}

if __name__ == "__main__":
    print("Starting TypeFlow API server...")
    uvicorn.run(app, host="0.0.0.0", port=80)