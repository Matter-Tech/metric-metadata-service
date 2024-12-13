import json

import pytest
from matter_api_client.http_client import delete, get, post, put


@pytest.mark.parametrize("server_url", ["properties"], indirect=True)
def test_get_property_by_id_endpoint(server_url, auth_bearer_jwt, property_id):
    response = get(url=f"{server_url}/{property_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"})
    assert response.status_code == 200
    assert response.json["id"] == property_id


@pytest.mark.parametrize("server_url", ["properties"], indirect=True)
def test_create_property_endpoint(server_url, auth_bearer_jwt):
    payload = {
        "propertyName": "longAbsoluteUnits",
        "propertyDescription": "Empty",
        "dataType": "string",
        "entityType": "metric",
        "isRequired": False,
    }

    response = post(url=server_url, payload=json.dumps(payload), headers={"Authorization": f"Bearer {auth_bearer_jwt}"})

    assert response.status_code == 201
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.parametrize("server_url", ["properties"], indirect=True)
def test_update_property_by_id_endpoint(server_url, auth_bearer_jwt, property_id):
    payload = {
        "propertyName": "longAbsolute",
    }

    response = put(
        url=f"{server_url}/{property_id}",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.parametrize("server_url", ["properties"], indirect=True)
def test_delete_property_by_id_endpoint(server_url, auth_bearer_jwt, property_id):
    response = delete(url=f"{server_url}/{property_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"})
    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None
    assert response_data["deletedAt"] is not None
