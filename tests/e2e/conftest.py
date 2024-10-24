import base64
import json

import pytest
from app.env import SETTINGS


@pytest.fixture()
def auth_bearer_jwt() -> str:
    payload = {
        "sub": "4s6f052mtcqg76tmfhba3ffhg6",
        "token_use": "access",
        "scope": "auth-api-v1/template-api:access",
        "auth_time": 1685522043,
        "iss": "https://cognito-idp.eu-central-1.amazonaws.com/eu-central-1_7Wmsf2K85",
        "exp": 1685525643,
        "iat": 1685522043,
        "version": 2,
        "jti": "d70aa8c2-54db-468a-8ee6-e2c8537c4846",
        "client_id": "4s6f052mtcqg76tmfhba3ffhg6",
    }

    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


@pytest.fixture(scope="session")
def server_url(request: pytest.FixtureRequest) -> str:
    return f"http://{SETTINGS.domain_name}{SETTINGS.path_prefix}/v1/{request.param}"
