"""
AccessOps Toolkit API
---------------------
FastAPI entry point for the AccessOps Toolkit.

Run with:
    uvicorn api.main:app --reload
"""

from fastapi import FastAPI

from api.routes.access import router as access_router


app = FastAPI(
    title="AccessOps Toolkit API",
    description="REST API for access auditing, provisioning, and removal workflows.",
    version="2.0.0",
)

app.include_router(access_router)

@app.get("/")
def root():
    return {
        "project": "AccessOps Toolkit",
        "status": "online",
        "docs": "/docs",
        "health": "/health"
    }
    
@app.get("/health", tags=["Health"])
def health_check() -> dict:
    return {
        "status": "healthy",
        "service": "accessops-toolkit-api",
        "version": "2.0.0",
    }