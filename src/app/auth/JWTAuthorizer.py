import logging
from datetime import datetime
from uuid import UUID

from fastapi import Depends, HTTPException, status

from .auth_header import decode_jwt
from .models import AuthorizedClient


class JWTAuthorizer:
    def __call__(
        self,
        payload: dict = Depends(decode_jwt),
    ) -> AuthorizedClient:
        """
        Parses valid JWT payload from Authorization header
        :param payload:
        :return: AuthorizedClient
        """

        if not (user_id := payload.get("https://auth.thisismatter.com/user/id")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if not (organization_id := payload.get("https://auth.thisismatter.com/org/id")):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            user_id = UUID(user_id)
        except Exception:
            logging.exception("The user ID is not in the right format")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            organization_id = UUID(organization_id)
        except Exception:
            logging.exception("The organization ID is not in the right format")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        permissions = payload.get("https://auth.thisismatter.com/permissions/", [])
        auth_client = AuthorizedClient(
            user_id=user_id,
            organization_id=organization_id,
            metadata=payload,
            permissions=permissions,
            created_at=datetime.fromtimestamp(payload["iat"]),
        )
        return auth_client
