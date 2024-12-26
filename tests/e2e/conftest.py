import json

import pytest
from app.env import SETTINGS
from matter_api_client.http_client import post


@pytest.fixture(scope="session")
def auth_bearer_jwt() -> str:
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtORm1PaDRXenoyZnRRVk1mNm42TCJ9.eyJodHRwczovL2F1dGgudGhpc2lzbWF0dGVyLmNvbS9vcmcvaWQiOiI0OTc2MWMwOS01ZThjLTViODQtYmFjMS1iYmY4ZDg1MjhmZWIiLCJodHRwczovL2F1dGgudGhpc2lzbWF0dGVyLmNvbS91c2VyL2lkIjoiODYxZDIwZTYtM2YzYi01MjI3LWE0YzItMWFmZGE3YTE1Mzc2IiwiaHR0cHM6Ly9hdXRoLnRoaXNpc21hdHRlci5jb20vcGVybWlzc2lvbnMvIjpbInBsYXRmb3JtOnB1YmxpYzpyZWFkIiwicGxhdGZvcm06cHVibGljOndyaXRlIiwicGxhdGZvcm06cHVibGljOmRlbGV0ZSIsInBsYXRmb3JtOnB1YmxpYy9lbnRpdHkvZmxhZ3M6cmVhZCIsInBsYXRmb3JtOm5hdGNhcDpvdmVyYWxsOmxpbWl0ZWQiLCJwbGF0Zm9ybTpwb3J0Zm9saW86c2hhcmUiLCJwbGF0Zm9ybTpwdWJsaWMvZW50aXR5L2ltcGFjdDpyZWFkIiwicGxhdGZvcm06ZGlzY2xvc3VyZV9kb2NzOmxpbmtzIiwicGxhdGZvcm06cGFydG5lcmFwaTphbGwiLCJwbGF0Zm9ybTppc3N1ZXJzYXBpOmFsbCIsInNpZ25hbHM6c2VudGltZW50OnJlYWQiLCJzaWduYWxzOmhvbGRpbmdzOmNydWQiLCJwbGF0Zm9ybTplbGVtZW50czphbGwiLCJzZmRyOnJlYWQiLCJzZGc6cHJlbWl1bTpyZWFkIiwicGxhdGZvcm06c3VwZXJ1c2VyOnJlYWQiLCJzZGc6cmVhZCIsInBsYXRmb3JtOnN1cGVydXNlcjp3cml0ZSIsInBsYXRmb3JtOnJhd19kYXRhOnJlYWQiXSwiaXNzIjoiaHR0cHM6Ly9hdXRoLnRoaXNpc21hdHRlci5jb20vIiwic3ViIjoiYXV0aDB8NjY3OTY3OTczODdlMWFkZmVhMjE2YTAwIiwiYXVkIjpbImh0dHBzOi8vdmFyYW51cy50aGlzaXNtYXR0ZXIuY29tIiwiaHR0cHM6Ly90aGlzaXNtYXR0ZXIuZXUuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTczMDY0MjA4NywiZXhwIjoxNzMwNzI4NDg3LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwib3JnX2lkIjoib3JnX1cwY0FjcmtiR3JqVGp4RVciLCJhenAiOiJvVFFZOFlubnhBeFI2TUEyMndtN1NzQ0pHcXRNNWdWOSJ9.ge_Pr7pUq1e4P-wk4I-XjaHPgw4twx96quHqfgCuKoQx3yXbSm3rCwKZkrCVuQYDsZHrUUVj1mGDMlx7lbARoknQ81_FXpRxCqXzC3Hu9bzC7CFGyWLWIBc7_Z3-dPEKKjt4LJWPGN8IHJ0HGoA3j2EDxEPHPQXPFegzkxfEOZzSG99o3zDY2P8IEqcP-60bjOZx2LYhlLUfAduFQSmxfQ7uEI-H7JbSGHGPv5JvwPPbSci_XGFgIHxLaxTWMLyNHHYhKRGqWy7-CI1GSDMMQrn2C5fl6SoTucNys2zEqjSJdwKqL9tTmM3llMnhMziYXf_4-ZBjgS2T1aH37ednPg"


@pytest.fixture(scope="session")
def server_url() -> str:
    return f"http://{SETTINGS.domain_name}{SETTINGS.path_prefix}/v1"


@pytest.fixture(scope="session")
def property_id(server_url, auth_bearer_jwt):
    # Create a new property and return its ID
    payload = {
        "propertyName": "testProperty",
        "propertyDescription": "Test Description",
        "dataType": "string",
        "entityType": "metric",
        "isRequired": False,
    }
    response = post(
        url=f"{server_url}/properties",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )
    assert response.status_code == 201
    return response.json["id"]


@pytest.fixture(scope="session")
def metric_set_id(server_url, auth_bearer_jwt):
    # Create a new property and return its ID
    payload = {
        "status": "deployed",
        "shortName": "Test_Metric_Set",
        "placement": "datasets/esgInsights",
        "metaData": {},
    }
    response = post(
        url=f"{server_url}/metric_sets",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )
    assert response.status_code == 201
    return response.json["id"]


@pytest.fixture(scope="session")
def metric_set_tree_id(server_url, auth_bearer_jwt, metric_set_id):
    # Create a new property and return its ID\
    payload = {
        "metricSetId": metric_set_id,
        "nodeType": "root",
        "nodeDepth": 0,
        "nodeName": "metric_set_tree_test",
        "nodeDescription": "Empty",
        "metaData": {},
    }
    response = post(
        url=f"{server_url}/metric_set_trees",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )
    assert response.status_code == 201
    return response.json["id"]


@pytest.fixture(scope="session")
def data_metric_id(server_url, auth_bearer_jwt):
    # Create a new property and return its ID
    payload = {
        "dataId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "metricType": "string",
        "name": "string",
        "metaData": {},
    }
    response = post(
        url=f"{server_url}/data_metrics",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )
    assert response.status_code == 201
    return response.json["id"]


@pytest.fixture(scope="session")
def metric_id(server_url, auth_bearer_jwt, data_metric_id, metric_set_id):
    # Create a new property and return its ID
    payload = {
        "metricSetId": metric_set_id,
        "dataMetricId": data_metric_id,
        "status": "deployed",
        "name": "test_metric",
        "nameSuffix": "tst_metr",
        "metaData": {},
    }
    response = post(
        url=f"{server_url}/metrics", payload=json.dumps(payload), headers={"Authorization": f"Bearer {auth_bearer_jwt}"}
    )
    assert response.status_code == 201
    return response.json["id"]


@pytest.fixture(scope="session")
def event_id(server_url, auth_bearer_jwt, metric_id):
    # Create a new property and return its ID
    payload = {
        "entityType": "metric",
        "nodeId": metric_id,
    }
    response = post(
        url=f"{server_url}/events/search",
        payload=json.dumps(payload),
        headers={"Authorization": f"Bearer {auth_bearer_jwt}"},
    )
    assert response.status_code == 200
    assert response.json["events"][0] is not None
    return response.json["events"][0]["id"]
