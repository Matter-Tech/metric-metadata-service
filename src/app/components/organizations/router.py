import uuid
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import JSONResponse
from matter_persistence.sql.utils import SortMethodModel

from app.authorization.organization import get_organization_id
from app.dependencies import Dependencies
from app.env import SETTINGS

from .dtos import (
    FullOrganizationOutDTO,
    OrganizationDeletionOutDTO,
    OrganizationInDTO,
    OrganizationListOutDTO,
    OrganizationOutDTO,
    OrganizationUpdateInDTO,
)
from .models.organization import OrganizationModel
from .models.organization_update import OrganizationUpdateModel
from .service import OrganizationService

organization_router = APIRouter(tags=["Organizations"], prefix=f"{SETTINGS.path_prefix}/v1/organizations")


@organization_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=OrganizationOutDTO,
    response_class=JSONResponse,
)
async def create_organization(
    organization_in_dto: OrganizationInDTO,
    organization_service: OrganizationService = Depends(Dependencies.organization_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Creates a new organization with the provided information.
    """
    organization_model = OrganizationModel.parse_obj(organization_in_dto)
    created_organization_model = await organization_service.create_organization(
        organization_model=organization_model,
        password=organization_in_dto.password,
        is_verified=True,
    )
    response_dto = OrganizationOutDTO.parse_obj(created_organization_model)

    return response_dto


@organization_router.get(
    "/{target_organization_id}",
    status_code=status.HTTP_200_OK,
    response_model=FullOrganizationOutDTO,
    response_class=JSONResponse,
)
async def get_organization(
    target_organization_id: Annotated[uuid.UUID, Path(title="The ID of the organization to retrieve")],
    organization_service: OrganizationService = Depends(Dependencies.organization_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Fetches the details of a organization.
    """
    organization_model = await organization_service.get_organization(organization_id=target_organization_id)
    response_dto = FullOrganizationOutDTO.parse_obj(organization_model)

    return response_dto


@organization_router.put(
    "/{target_organization_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationOutDTO,
    response_class=JSONResponse,
)
async def update_organization(
    target_organization_id: Annotated[uuid.UUID, Path(title="The ID of the organization to update")],
    organization_in_dto: OrganizationUpdateInDTO,
    organization_service: OrganizationService = Depends(Dependencies.organization_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Update the organization's details with the specified data.
    """
    organization_update_model = OrganizationUpdateModel.parse_obj(organization_in_dto)
    updated_organization_model = await organization_service.update_organization(
        organization_id=target_organization_id,
        organization_update_model=organization_update_model,
    )
    response_dto = OrganizationOutDTO.parse_obj(updated_organization_model)

    return response_dto


@organization_router.delete(
    "/{target_organization_id}",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationDeletionOutDTO,
    response_class=JSONResponse,
)
async def delete_organization(
    target_organization_id: Annotated[uuid.UUID, Path(title="The ID of the organization to delete")],
    organization_service: OrganizationService = Depends(Dependencies.organization_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Deletes a organization with the given target_organization_id.
    """
    deleted_organization_model = await organization_service.delete_organization(organization_id=target_organization_id)
    response_dto = OrganizationDeletionOutDTO.parse_obj(deleted_organization_model)

    return response_dto


@organization_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationListOutDTO,
    response_class=JSONResponse,
)
async def find_organizations(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(
        SETTINGS.pagination_limit_default,
        ge=0,
        le=SETTINGS.pagination_limit_max,
        description="Number of items to retrieve",
    ),
    sort_field: str = Query(None, title="Sort field", description="Field to sort by"),
    sort_method: SortMethodModel = Query(
        SortMethodModel.ASC, title="Sort method", description="Sort method: asc or desc"
    ),
    with_deleted: bool | None = Query(False, description="Include deleted organizations"),
    organization_service: OrganizationService = Depends(Dependencies.organization_service),
    organization_id: UUID = Depends(get_organization_id),
):
    """
    Return a list of organizations, based on given parameters.
    """
    organizations = await organization_service.find_organizations(
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_method=sort_method,
        with_deleted=with_deleted,
    )
    response_dto = OrganizationListOutDTO(
        count=len(organizations),
        organizations=FullOrganizationOutDTO.parse_obj(organizations),
    )

    return response_dto
