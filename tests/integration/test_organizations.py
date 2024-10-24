import pytest
from app.components.organizations.models.organization import OrganizationModel
from app.components.organizations.models.organization_update import OrganizationUpdateModel
from app.components.organizations.service import OrganizationService
from matter_persistence.sql.exceptions import DatabaseRecordNotFoundError
from matter_persistence.sql.utils import SortMethodModel


@pytest.mark.asyncio
async def test_create_and_delete_organization_in_database(
    organization: OrganizationModel,
    organization_service: OrganizationService,
):
    # When
    organization.id = None
    created_organization = await organization_service.create_organization(
        organization_model=organization,
    )

    retrieved_organization = await organization_service._dal.get_organization(created_organization.id)
    assert isinstance(organization, OrganizationModel)

    # Then
    assert retrieved_organization.id == created_organization.id
    assert (
        retrieved_organization.organization_name
        == created_organization.organization_name
        == organization.organization_name
    )
    assert (
        retrieved_organization.organization_email
        == created_organization.organization_email
        == organization.organization_email
    )
    assert retrieved_organization.first_name == created_organization.first_name == organization.first_name
    assert retrieved_organization.last_name == created_organization.last_name == organization.last_name

    # Soft delete
    deleted_organization = await organization_service.delete_organization(created_organization.id)
    deleted_organization = await organization_service._dal.get_organization(deleted_organization.id)
    assert deleted_organization.deleted is not None

    # Hard delete
    deleted_organization = await organization_service._dal.delete_organization(
        deleted_organization.id, soft_delete=False
    )
    with pytest.raises(DatabaseRecordNotFoundError):
        await organization_service._dal.get_organization(deleted_organization.id)


@pytest.mark.asyncio
async def test_get_organization_from_database(
    organization_service: OrganizationService,
):
    # When
    result = await organization_service.find_organizations()
    assert len(result) > 0

    organization = await organization_service.get_organization(result[0].id)
    assert isinstance(organization, OrganizationModel)

    # Then
    assert organization.id == result[0].id
    assert organization.organization_email == result[0].organization_email
    assert organization.organization_name == result[0].organization_name
    assert organization.first_name == result[0].first_name
    assert organization.last_name == result[0].last_name


@pytest.mark.asyncio
async def test_find_organizations_in_database(
    organization_service: OrganizationService,
):
    # When
    result = await organization_service.find_organizations(
        skip=2,
        limit=2,
        sort_field="organization_email",
        sort_method=SortMethodModel.ASC,
        with_deleted=False,
    )

    # Then
    assert len(result) == 2
    assert result[0].organization_email == "app@website.com"
    assert result[1].organization_email == "manager@website.com"


@pytest.mark.asyncio
async def test_find_organizations_in_database_desc(
    organization_service: OrganizationService,
):
    # When
    result = await organization_service.find_organizations(
        skip=1,
        limit=3,
        sort_field="organization_email",
        sort_method=SortMethodModel.DESC,
        with_deleted=False,
    )

    # Then
    assert len(result) == 3
    assert result[0].organization_email == "manager@website.com"
    assert result[1].organization_email == "app@website.com"
    assert result[2].organization_email == "api@website.com"


@pytest.mark.asyncio
async def test_update_organization_in_database(
    organization: OrganizationModel,
    organization_service: OrganizationService,
):
    # When
    organization.id = None
    created_organization = await organization_service.create_organization(
        organization_model=organization,
    )

    updated_organization = await organization_service.update_organization(
        organization_id=created_organization.id,
        organization_update_model=OrganizationUpdateModel(
            first_name="John",
            last_name="Doe",
            organization_name="Example Organization",
            organization_email="john.doe@example.com",
        ),
    )

    updated_organization = await organization_service._dal.get_organization(updated_organization.id)

    # Then
    assert updated_organization.id == created_organization.id
    assert updated_organization.organization_email == "john.doe@example.com"
    assert updated_organization.organization_name == "Example Organization"
    assert updated_organization.first_name == "John"
    assert updated_organization.last_name == "Doe"
    assert updated_organization.updated is not None

    # Hard delete
    await organization_service._dal.delete_organization(updated_organization.id, soft_delete=False)
