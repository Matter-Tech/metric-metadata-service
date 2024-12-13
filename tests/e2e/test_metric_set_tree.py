import json

import pytest
from matter_api_client.http_client import delete, get, post, put


@pytest.mark.usefixtures("server_url", indirect=True)
def test_get_metric_set_tree_by_id_endpoint(server_url, auth_bearer_jwt, metric_set_tree_id):
    response = get(
        url=f"{server_url}/metric_set_trees/{metric_set_tree_id}",
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )
    assert response.status_code == 200
    assert response.json["id"] == metric_set_tree_id


@pytest.mark.usefixtures("server_url", indirect=True)
def test_create_metric_set_tree_endpoint(server_url, auth_bearer_jwt, metric_set_id):
    payload = {
        "nodeName": "NormalValue",
        "nodeDescription": "Empty",
        "nodeDepth": 0,
        "nodeType": "root",
        "metricSetId": metric_set_id,
        "metaData": {},
    }

    response = post(
        url=f"{server_url}/metric_set_trees",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 201
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_update_metric_set_tree_by_id_endpoint(server_url, auth_bearer_jwt, metric_set_tree_id):
    payload = {
        "nodeName": "UpdatedValue",
    }

    response = put(
        url=f"{server_url}/metric_set_trees/{metric_set_tree_id}",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_delete_metric_set_tree_by_id_endpoint(server_url, auth_bearer_jwt, metric_set_tree_id):
    response = delete(
        url=f"{server_url}/metric_set_trees/{metric_set_tree_id}",
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )
    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["id"] is not None
    assert response_data["deletedAt"] is not None


@pytest.mark.usefixtures("server_url", indirect=True)
def test_search_metric_set_tree(server_url, auth_bearer_jwt):
    response = post(
        url=f"{server_url}/metric_set_trees/search",
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )

    assert response.status_code == 200
    response_data = response.json
    assert response_data["createdAt"] is not None
    assert response_data["createdAtTimestamp"] is not None
    assert response_data["count"] is not None
