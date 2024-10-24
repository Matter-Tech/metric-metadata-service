from datetime import datetime, timezone
from typing import List
from uuid import UUID

from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.manager import DatabaseManager
from matter_persistence.sql.utils import SortMethodModel, commit, find, get
from sqlalchemy import select

from app.components.organizations.models.organization import OrganizationModel
from app.components.organizations.models.organization_update import OrganizationUpdateModel


class OrganizationDAL:
    """
    The OrganizationDAL class provides methods for interacting with the database to perform CRUD operations on OrganizationModel objects.

    Attributes:
        _db_session (DatabaseSessionManager): The database session manager for managing database sessions.

    Methods:
        get_organization:
            Retrieves an organization from the database based on the organization ID.

            Parameters:
                organization_id (UUID): The ID of the organization to retrieve.
                with_email_verification (bool, optional): Whether to include the email verification information of the organization. Defaults to False.

            Returns:
                OrganizationModel: The retrieved organization model.

            Raises:
                DatabaseRecordNotFoundError: If the organization model with the given ID is not found in the database.

        find_organizations:
            Retrieves a list of organizations from the database based on optional filters.

            Parameters:
                skip (int, optional): The number of organizations to skip. Defaults to 0.
                limit (int, optional): The maximum number of organizations to retrieve. Defaults to None.
                sort_field (str, optional): The field to sort the organizations by. Defaults to None.
                sort_method (SortMethodModel, optional): The sort method to use. Defaults to None.
                with_deleted (bool, optional): Whether to include the soft deleted organizations. Defaults to True.
                filters (dict | None, optional): Additional filters to apply for retrieving organizations. Defaults to None.

            Returns:
                List[OrganizationModel]: The list of retrieved organization models.

        create_organization:
            Creates a new organization in the database.

            Parameters:
                organization_model (OrganizationModel): The organization model to create.

            Returns:
                OrganizationModel: The created organization model.

        update_organization:
            Updates an existing organization in the database.

            Parameters:
                organization_id (UUID): The ID of the organization to update.
                organization_update_model (OrganizationUpdateModel): The organization update model containing the updated information.

            Returns:
                OrganizationModel: The updated organization model.

        delete_organization:
            Deletes an organization from the database.

            Parameters:
                organization_id (UUID): The ID of the organization to delete.
                soft_delete (bool, optional): Whether to perform a soft delete. Defaults to True.

            Returns:
                OrganizationModel: The deleted organization model.

    """

    def __init__(
        self,
        database_manager: DatabaseManager,
    ):
        self._database_manager = database_manager

    async def get_organization(
        self,
        organization_id: UUID,
    ) -> OrganizationModel:
        statement = select(OrganizationModel).where(OrganizationModel.id == organization_id)

        async with self._database_manager.session() as session:
            organization_model = await get(
                session=session,
                statement=statement,
            )

            if organization_model is None:
                raise DatabaseRecordNotFoundError(
                    description=f"OrganizationModel with Organization Id '{organization_id}' not found.",
                    detail={
                        "organization_id": organization_id,
                    },
                )

            return organization_model

    async def find_organizations(
        self,
        skip: int = 0,
        limit: int = None,
        sort_field: str = None,
        sort_method: SortMethodModel = None,
        with_deleted: bool = True,
        filters: dict | None = None,
    ) -> List[OrganizationModel]:
        async with self._database_manager.session() as session:
            return await find(
                session=session,
                db_model=OrganizationModel,
                skip=skip,
                limit=limit,
                sort_field=sort_field,
                sort_method=sort_method,
                with_deleted=with_deleted,
                filters=filters,
            )

    async def create_organization(self, organization_model: OrganizationModel) -> OrganizationModel:
        async with self._database_manager.session() as session:
            session.add(organization_model)
            await commit(session)

        return organization_model

    async def update_organization(
        self,
        organization_id: UUID,
        organization_update_model: OrganizationUpdateModel,
    ) -> OrganizationModel:
        organization_model = await self.get_organization(organization_id)

        async with self._database_manager.session() as session:
            organization_model = await session.merge(organization_model)
            for k, v in organization_update_model.model_dump().items():
                if k not in [
                    "created",
                    "deleted",
                    "updated",
                ]:  # updated & created are handled by sqlalchemy; deleted is handled by user
                    if hasattr(organization_model, k):
                        setattr(organization_model, k, v)

            await commit(session)

        return organization_model

    async def delete_organization(
        self,
        organization_id: UUID,
        soft_delete: bool = True,
    ) -> OrganizationModel:
        organization_model = await self.get_organization(organization_id)

        async with self._database_manager.session() as session:
            organization_model = await session.merge(organization_model)
            if soft_delete:
                organization_model.deleted = datetime.now(tz=timezone.utc)
            else:
                await session.delete(organization_model)

            await commit(session)

            if organization_model.deleted is None:
                organization_model.deleted = datetime.now(tz=timezone.utc)

        return organization_model
