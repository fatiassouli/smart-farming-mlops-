"""
Monitoring & Observabilité pour l'API Smart Farming.
Ajoute des logs structurés JSON, health check et métriques basiques.
"""

import logging
import time
import json
from datetime import datetime
from fastapi import Request


# ═══════════════════════════════════════════════════════
# Configuration des logs structurés JSON
# ═══════════════════════════════════════════════════════
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_obj.update(record.extra)
        return json.dumps(log_obj, ensure_ascii=False)


def setup_monitoring(app):
    """Configure le monitoring sur l'application FastAPI."""
    
    # Logger structuré
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger = logging.getLogger("smart_farming_api")
    logger.handlers = []
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # ═══════════════════════════════════════════════════
    # Middleware : log chaque requête (temps, status, etc.)
    # ═══════════════════════════════════════════════════
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        
        response = await call_next(request)
        duration = time.time() - start
        
        logger.info(
            "Request processed",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client": request.client.host if request.client else "unknown",
            }
        )
        return response

    # ═══════════════════════════════════════════════════
    # Endpoint /health détaillé
    # ═══════════════════════════════════════════════════
    @app.get("/health", tags=["Monitoring"])
    def health():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "smart-farming-api",
            "version": "1.0.0",
        }

    # ═══════════════════════════════════════════════════
    # Endpoint /metrics basique
    # ═══════════════════════════════════════════════════
    @app.get("/metrics", tags=["Monitoring"])
    def metrics():
        return {
            "service": "smart-farming-api",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Pour Prometheus complet, ajouter prometheus-client",
        }
