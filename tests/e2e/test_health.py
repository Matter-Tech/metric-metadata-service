import pytest
from matter_api_client.http_client import get


@pytest.mark.parametrize("server_url", ["health"], indirect=True)
def test_health_endpoint(server_url):
    response = get(server_url.replace("/template-api/v1", ""))
    assert response.status_code == 200
    assert response.json == {"health": True}


@pytest.mark.parametrize("server_url", ["health/deep"], indirect=True)
def test_health_endpoint_deep(server_url):
    response = get(server_url.replace("/template-api/v1", ""))
    assert response.status_code == 200
    assert response.json["health"] is True
    assert response.json["database"] is True
    assert response.json["cache"] is True
