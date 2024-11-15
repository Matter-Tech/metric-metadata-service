from contextvars import ContextVar, Token

from fastapi import Depends

from .auth_header import decode_jwt
from .JWTAuthorizer import JWTAuthorizer
from .models import AuthorizedClient

_request_client_ctx_var: ContextVar[AuthorizedClient] = ContextVar("authorized_client")


def set_request_client(client: AuthorizedClient) -> Token:
    token = _request_client_ctx_var.set(client)
    return token


def get_request_client() -> AuthorizedClient:
    return _request_client_ctx_var.get()


async def jwt_authorizer(payload: dict = Depends(decode_jwt)):
    client = JWTAuthorizer()(payload)
    set_request_client(client)
    return client
