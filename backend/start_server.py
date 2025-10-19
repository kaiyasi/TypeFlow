#!/usr/bin/env python3

import sys
import os

# Set up Python path
sys.path.insert(0, '/app')
os.chdir('/app')

# Set environment variables  
os.environ['PYTHONPATH'] = '/app'

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    
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
        return {
            "message": "TypeFlow API",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/healthz")
    async def health_check():
        return {"status": "healthy", "service": "typeflow-api"}
    
    @app.get("/api/")
    async def api_root():
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
        return {"user": None, "authenticated": False}
    
    # Run the server
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=80)

except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)