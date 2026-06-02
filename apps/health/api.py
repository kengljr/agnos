import logging
from ninja import Router
from .schema import HealthResponse
from .models import ApiLog

router = Router(tags=["health"])
logger = logging.getLogger(__name__)

@router.get(
    "/health",
    response = HealthResponse,
)

def health_check(request):
    logger.info("Health endpoint called")
    return {
        "status":"UP"
    }