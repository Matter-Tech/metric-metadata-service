import uuid
from typing import List

from matter_exceptions.exceptions.fastapi import ServerError
from matter_observability.metrics import (
    count_occurrence,
    measure_processing_time,
)
from matter_persistence.sql.exceptions import DatabaseError
from matter_persistence.sql.utils import SortMethodModel

from app.components.organizations.dal import OrganizationDAL
from app.components.organizations.models.organization import OrganizationModel
from app.components.organizations.models.organization_update import OrganizationUpdateModel


class OrganizationService:
    """
    Class: OrganizationService

    This class represents a service for interacting with organizations in a system.

    Methods:
    - get_organization(organization_id: uuid.UUID) -> OrganizationModel:
        Retrieves an organization by its ID. Returns the organization model.
    - find_organizations(skip: int = 0, limit: int = None, sort_field: str | None = None,
      sort_method: SortMethodModel | None = None, with_deleted: bool = False) -> List[OrganizationModel]:
        Finds organizations based on optional parameters such as skip, limit, sorting, and deleted status.
        Returns a list of organization models.
    - create_organization(organization_model: OrganizationModel) -> OrganizationModel:
        Creates a new organization using the provided organization model.
        If a database error occurs, a ServerError is raised with details from the DatabaseError.
        Returns the created organization model.
    - update_organization(organization_id: uuid.UUID, organization_update_model: OrganizationUpdateModel) -> OrganizationModel:
        Updates an existing organization with the provided update model.
        Returns the updated organization model.
    - delete_organization(organization_id: uuid.UUID) -> OrganizationModel:
        Deletes an organization by its ID. Soft delete is performed by default.
        Returns the deleted organization model.

    Attributes:
    - dal: OrganizationDAL: The data access layer used by the service.

    """

    def __init__(
        self,
        dal: OrganizationDAL,
    ):
        self._dal = dal

    @count_occurrence(label="organizations.get_organization")
    @measure_processing_time(label="organizations.get_organization")
    async def get_organization(
        self,
        organization_id: uuid.UUID,
    ) -> OrganizationModel:
        return await self._dal.get_organization(organization_id)

    @count_occurrence(label="organizations.find_organizations")
    @measure_processing_time(label="organizations.find_organizations")
    async def find_organizations(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str | None = None,
        sort_method: SortMethodModel | None = None,
        with_deleted: bool = False,
    ) -> List[OrganizationModel]:
        return await self._dal.find_organizations(
            skip=skip,
            limit=limit,
            sort_field=sort_field,
            sort_method=sort_method,
            with_deleted=with_deleted,
        )

    @count_occurrence(label="organizations.create_organization")
    @measure_processing_time(label="organizations.create_organization")
    async def create_organization(
        self,
        organization_model: OrganizationModel,
    ) -> OrganizationModel:
        try:
            created_organization_model = await self._dal.create_organization(organization_model)
        except DatabaseError as ex:
            raise ServerError(description=ex.description, detail=ex.detail)

        return created_organization_model

    @count_occurrence(label="organizations.update_organization")
    @measure_processing_time(label="organizations.update_organization")
    async def update_organization(
        self,
        organization_id: uuid.UUID,
        organization_update_model: OrganizationUpdateModel,
    ) -> OrganizationModel:
        return await self._dal.update_organization(organization_id, organization_update_model)

    @count_occurrence(label="organizations.delete_organization")
    @measure_processing_time(label="organizations.delete_organization")
    async def delete_organization(
        self,
        organization_id: uuid.UUID,
    ) -> OrganizationModel:
        return await self._dal.delete_organization(organization_id, soft_delete=True)
