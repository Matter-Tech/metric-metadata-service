import uuid

import pytest
from matter_api_client.http_client_async import get, post


@pytest.mark.asyncio
@pytest.mark.parametrize("server_url", ["items/hello"], indirect=True)
async def test_items_async_flow_random_id(
    server_url: str,
    auth_bearer_jwt: str,
):
    payload = {}  # empty json, to create a random Id

    post_response = await post(
        url=server_url,
        headers={"jwt": auth_bearer_jwt},
        payload=payload,
    )

    assert post_response.status_code == 201

    item_id = post_response.json["id"]

    get_response = await get(
        url=f"{server_url}?item_id={item_id}",
        headers={"jwt": auth_bearer_jwt},
    )

    assert get_response.status_code == 200
    assert get_response.json["createdAt"] == post_response.json["createdAt"]
    assert get_response.json["createdAtTimestamp"] == post_response.json["createdAtTimestamp"]
    assert get_response.json["id"] == post_response.json["id"]
    assert get_response.json["value"] == "My New Generated Value"


@pytest.mark.asyncio
@pytest.mark.parametrize("server_url", ["items/hello"], indirect=True)
async def test_items_async_flow_defined_id(
    server_url: str,
    auth_bearer_jwt: str,
):
    defined_id = uuid.uuid4()
    payload = {"id": str(defined_id)}  # set an external id

    post_response = await post(
        url=server_url,
        headers={"jwt": auth_bearer_jwt},
        payload=payload,
    )

    assert post_response.status_code == 201

    item_id = post_response.json["id"]

    assert item_id == str(defined_id)

    get_response = await get(
        url=f"{server_url}?item_id={item_id}",
        headers={"jwt": auth_bearer_jwt},
    )

    assert get_response.status_code == 200
    assert get_response.json["createdAt"] == post_response.json["createdAt"]
    assert get_response.json["createdAtTimestamp"] == post_response.json["createdAtTimestamp"]
    assert get_response.json["id"] == post_response.json["id"]
    assert get_response.json["value"] == "My New Generated Value"
