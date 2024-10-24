import pytest
from matter_api_client.http_client import get


@pytest.mark.parametrize("server_url", ["organizations"], indirect=True)
def test_auth_with_organization_id_should_return_ok(server_url, auth_bearer_jwt):
    response = get(url=server_url, headers={"jwt": auth_bearer_jwt})

    assert response.status_code == 200


@pytest.mark.parametrize("server_url", ["organizations"], indirect=True)
def test_auth_without_organization_id_should_return_unauthorized(server_url):
    response = get(server_url)

    assert response.status_code == 401
