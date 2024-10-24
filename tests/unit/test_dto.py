import pytest
from app.components.organizations.dtos import OrganizationInDTO, OrganizationUpdateInDTO
from pydantic import ValidationError


def test_organization_dto():
    """An Organization Model should be fully constructable from JSON"""
    dto = {
        "organizationName": "MyOrganization",
        "organizationEmail": "user@example.com",
        "firstName": "FirstName",
        "lastName": "LastName",
    }

    OrganizationInDTO(**dto)


def test_organization_dto_invalid_email():
    """An Organization Model should raise a ValidationError if the email is invalid"""
    dto = {
        "organizationName": "MyOrganization",
        "organizationEmail": "invalid_email",
        "firstName": "FirstName",
        "lastName": "LastName",
    }

    with pytest.raises(ValidationError) as exc_info:
        OrganizationInDTO(**dto)

    assert "organizationEmail" in str(exc_info.value)


def test_organization_update_dto():
    """An Organization Update Model should be fully constructable from JSON"""
    dto = {
        "organizationName": "MyOrganization",
        "firstName": "FirstName",
        "lastName": "LastName",
    }

    OrganizationUpdateInDTO(**dto)
