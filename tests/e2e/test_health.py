import pytest
from matter_api_client.http_client import get


@pytest.mark.usefixtures("server_url", indirect=True)
def test_health_endpoint(server_url):
    response = get(url=f"{server_url.replace("/metric-metadata-service/v1", "")}/health")
    assert response.status_code == 200
    assert response.json == {"health": True}


@pytest.mark.usefixtures("server_url", indirect=True)
def test_health_endpoint_deep(server_url):
    response = get(url=f"{server_url.replace("/metric-metadata-service/v1", "")}/health/deep")
    assert response.status_code == 200
    assert response.json["health"] is True
    assert response.json["database"] is True
    assert response.json["cache"] is True
