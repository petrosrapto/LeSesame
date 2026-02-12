"""
Le Sésame Backend - Health Check Router

Author: Petros Raptopoulos
Date: 2026/02/06
"""

from fastapi import APIRouter
from datetime import datetime

from ..services.llm import get_structured_output_metrics

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


@router.get("/metrics/structured-output")
async def structured_output_metrics():
    """
    Get metrics about structured output success rates.

    Use this endpoint to monitor which fallback tier is being used:
    - High json_schema_success_rate (>95%) = Good, primary method working
    - High default_method_success_rate = Fallback being used frequently (investigate)
    - High manual_parse_success_rate = Both structured methods failing (critical)
    - Low overall_success_rate (<90%) = Critical issue, system degraded
    """
    metrics = get_structured_output_metrics()

    # Determine health status based on metrics
    total = metrics.get("total_calls", 0)
    if total == 0:
        status = "no_data"
    elif metrics.get("json_schema_success_rate", 0) > 95:
        status = "healthy"
    elif metrics.get("overall_success_rate", 0) > 90:
        status = "degraded"
    else:
        status = "critical"

    return {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics,
    }
