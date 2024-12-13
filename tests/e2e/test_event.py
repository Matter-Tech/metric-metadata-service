import pytest
from matter_api_client.http_client import delete, get, post


@pytest.mark.usefixtures("server_url", indirect=True)
def test_get_event_by_id_endpoint(server_url, auth_bearer_jwt, event_id):
    response = get(url=f"{server_url}/events/{event_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"})
    assert response.status_code == 200
    assert response.json["id"] == event_id


@pytest.mark.usefixtures("server_url", indirect=True)
def test_delete_event_by_id_endpoint(server_url, auth_bearer_jwt, event_id):
    response = delete(url=f"{server_url}/events/{event_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"})
    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None
    assert response_data["deletedAt"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_search_event(server_url, auth_bearer_jwt):
    response = post(
        url=f"{server_url}/events/search",
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["count"] is not None
