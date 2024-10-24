from contextvars import ContextVar, Token
from uuid import UUID

from .models import IdentityModel

_request_user_ctx_var: ContextVar[IdentityModel] = ContextVar("authorized_user")


def set_identity(identity: IdentityModel) -> Token:
    return _request_user_ctx_var.set(identity)


def get_identity() -> IdentityModel:
    return _request_user_ctx_var.get()


def get_request_organization_id() -> UUID:
    return get_identity().organization_id
