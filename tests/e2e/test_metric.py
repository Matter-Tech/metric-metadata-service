import json

import pytest
from matter_api_client.http_client import delete, get, post, put


@pytest.mark.usefixtures("server_url", indirect=True)
def test_get_metric_by_id_endpoint(server_url, auth_bearer_jwt, metric_id):
    response = get(url=f"{server_url}/metrics/{metric_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"})
    assert response.status_code == 200
    assert response.json["id"] == metric_id


@pytest.mark.usefixtures("server_url", indirect=True)
def test_create_metric_endpoint(server_url, auth_bearer_jwt, metric_set_id, data_metric_id):
    payload = {
        "metricSetId": metric_set_id,
        "dataMetricId": data_metric_id,
        "status": "deployed",
        "name": "CreatedName",
        "nameSuffix": "CrN",
        "metaData": {},
    }

    response = post(
        url=f"{server_url}/metrics", payload=json.dumps(payload), headers={"Authorization": f"Bearer {auth_bearer_jwt}"}
    )

    assert response.status_code == 201
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_update_metric_by_id_endpoint(server_url, auth_bearer_jwt, metric_id):
    payload = {
        "name": "UpdatedName",
    }

    response = put(
        url=f"{server_url}/metrics/{metric_id}",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_delete_metric_by_id_endpoint(server_url, auth_bearer_jwt, metric_id):
    response = delete(url=f"{server_url}/metrics/{metric_id}", headers={"Authorization": f"Bearer {auth_bearer_jwt}"})
    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None
    assert response_data["deletedAt"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_search_metric(server_url, auth_bearer_jwt):
    response = post(
        url=f"{server_url}/metrics/search",
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["count"] is not None
