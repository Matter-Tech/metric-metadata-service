import base64
import binascii
import json
import logging

from fastapi import Request
from matter_api_client.exceptions import APIClientError
from matter_api_client.http_client_async import get
from matter_exceptions.exceptions.fastapi import ServerError, UnauthorizedError
from matter_exceptions.utils import capture_error
from matter_persistence.redis.exceptions import CacheRecordNotFoundError

from app.env import SETTINGS

from .models import IdentityModel


async def decode_jwt(request: Request) -> IdentityModel:
    # no need for fancy jwt features, just decode it from the headers
    encoded_jwt_access_token = request.headers.get("jwt")
    if not encoded_jwt_access_token:
        raise UnauthorizedError(description="JWT token is missing from headers. Make sure to include it under 'jwt'")

    from app.dependencies import Dependencies

    cache_manager = Dependencies.cache_manager()
    try:
        identity_model = await cache_manager.get_with_key(
            key=encoded_jwt_access_token,
            object_class=IdentityModel,
        )
        logging.info("Retrieved JWT identity from cache.")
        return identity_model
    except CacheRecordNotFoundError:
        logging.info("Unable to retrieve JWT identity from cache, therefore connecting to the Auth API.")

    try:
        logging.debug(f"Encoded JWT Token: {encoded_jwt_access_token}")
        decoded_jwt_access_token = json.loads(
            base64.standard_b64decode(encoded_jwt_access_token + "=" * (4 - len(encoded_jwt_access_token) % 4))
        )
    except (binascii.Error, UnicodeDecodeError) as ex:
        logging.error(f"JWT decoding failed: {str(ex)}")
        raise UnauthorizedError(
            description=f"Invalid JWT Token: {str(ex)}",
            detail={"token": encoded_jwt_access_token},
        )

    try:
        client_id = decoded_jwt_access_token["sub"]
    except KeyError:
        logging.error("JWT decoding failed: sub (client_id) is missing.")
        raise UnauthorizedError(
            description="Invalid JWT Token: client_id is missing.",
            detail={"token": encoded_jwt_access_token},
        )

    try:
        response = await get(url=f"{SETTINGS.auth_api_url}/v1/admin/whois/{client_id}")
        # TODO: Remove mock data generation
        # from matter_api_client.response import Response
        # response = Response(
        #     status_code=200,
        #     text="""
        #     {
        #         "id": "5aa4491c-4cf8-40aa-be86-d6d8f2b9381d",
        #         "client_id": "TGVrJBCCvn",
        #         "created_at": "2023-04-14T11:45:10.898606",
        #         "last_time_used": "2023-04-14T11:45:57.978078",
        #         "organization_id": "3f46658a-19c3-4410-96e5-e21c581a0567"
        #     }
        #     """
        # )
        # import orjson
        # response.json = orjson.loads(response.text)
    except APIClientError as ex:
        raise ServerError(description=f"Unable to connect to the Auth API: {str(ex)}.")
    else:
        if response.status_code != 200:
            error_description = f"Unable to authenticate token: Auth API returned a {response.status_code} Status Code: {response.text}."
            capture_error(
                error_description,
                extra={
                    "response": response.__dict__,
                    "encoded_jwt": encoded_jwt_access_token,
                    "decoded_jwt": decoded_jwt_access_token,
                },
            )
            raise UnauthorizedError(
                description=error_description,
                detail=response.json,
            )

    identity_model = IdentityModel.parse_obj(response.json)
    await cache_manager.save_with_key(
        key=encoded_jwt_access_token,
        value=identity_model,
        object_class=IdentityModel,
        expiration_in_seconds=SETTINGS.cache_token_expiration,
    )

    return identity_model
