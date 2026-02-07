"""
Le Sésame Backend - Health Check Router

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "le-sesame-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "status": "ready",
        "service": "le-sesame-api",
        "timestamp": datetime.utcnow().isoformat()
    }
