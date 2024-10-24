from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.dependencies import Dependencies

from .dtos import HealthDeepStatusOutDTO, HealthStatusOutDTO
from .service import HealthService

health_router = APIRouter(tags=["Health"], prefix="/health")


@health_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=HealthStatusOutDTO,
    response_class=JSONResponse,
)
async def shallow_health(
    health_service: HealthService = Depends(Dependencies.health_service),
):
    """
    Returns the general health status of the API.
    """
    health_status_model = await health_service.get_health_status()
    return HealthStatusOutDTO(**health_status_model.model_dump())


@health_router.get(
    "/deep",
    status_code=status.HTTP_200_OK,
    response_model=HealthDeepStatusOutDTO,
    response_class=JSONResponse,
)
async def deep_healthcheck(
    health_service: HealthService = Depends(Dependencies.health_service),
):
    """
    Returns the general health status of the API.
    """
    health_status_model = await health_service.get_health_status()
    return HealthDeepStatusOutDTO.parse_obj(health_status_model)
