import base64
import json
import logging

from fastapi import HTTPException, Request


def decode_jwt(request: Request) -> dict:
    # no need for fancy jwt features, just decode it from the headers

    try:
        encoded = (
            request.headers.get("authorization").split(" ")[1].split(".")[1]
            or request.headers.get("jwt")
            or request.headers.get("x-jwt-e2e")
        )
        decoded = json.loads(base64.standard_b64decode(encoded + "=" * (4 - len(encoded) % 4)))
    except Exception:
        logging.exception("Not possible to decode the JWT.")
        raise HTTPException(status_code=401, detail="Invalid token")
    else:
        return decoded
