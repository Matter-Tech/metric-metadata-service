import json

import pytest
from matter_api_client.http_client import delete, get, post, put


@pytest.mark.usefixtures("server_url", indirect=True)
def test_get_data_metric_by_id_endpoint(server_url, auth_bearer_jwt, data_metric_id):
    response = get(
        url=f"{server_url}/data_metrics/{data_metric_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"}
    )
    assert response.status_code == 200
    assert response.json["id"] == data_metric_id


@pytest.mark.usefixtures("server_url", indirect=True)
def test_create_data_metric_endpoint(server_url, auth_bearer_jwt):
    payload = {
        "dataId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "metricType": "impact_metric_universal",
        "name": "test_data_metric",
        "metaData": {},
    }

    response = post(
        url=f"{server_url}/data_metrics",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 201
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_update_data_metric_by_id_endpoint(server_url, auth_bearer_jwt, data_metric_id):
    payload = {
        "name": "updated_test_data_metric",
    }

    response = put(
        url=f"{server_url}/data_metrics/{data_metric_id}",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_delete_data_metric_by_id_endpoint(server_url, auth_bearer_jwt, data_metric_id):
    response = delete(
        url=f"{server_url}/data_metrics/{data_metric_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"}
    )
    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None
    assert response_data["deletedAt"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_search_metric(server_url, auth_bearer_jwt):
    response = post(
        url=f"{server_url}/data_metrics/search",
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["count"] is not None
