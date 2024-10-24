from typing import Annotated, Literal

from pydantic import StringConstraints
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment Settings
    env: Literal["local", "test", "dev", "prod"] = "local"
    debug: bool = False

    # Server configuration
    server_port: int = 8080
    server_log_level: str = "info"
    path_prefix: str = ""
    instance_name: str = ""
    domain_name: str = ""

    # Security - JWT
    secret_key: str = "secret-key"  # openssl rand -hex 32
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Services
    auth_api_url: str

    # Database configuration
    db_url: str
    pg_connpoolsize: int = 10
    migrations_folder: str

    # Pagination
    pagination_limit_max: int = 1000
    pagination_limit_default: int = 100

    # Cache
    cache_endpoint_url: str
    cache_port: int = 6379
    cache_default_record_expiration: int = 60 * 60 * 24  # 24 hours
    cache_token_expiration: int = 3600 * 1  # 1 hour
    cache_error_expiration: int = 60 * 15
    cache_lock_expiration: int = 10
    cache_flag_expiration: int = 60 * 10

    # Observability
    prometheus_push_gateway_host: str
    sentry_dsn: str
    default_tracing_sample_rate: float = 0.1
    enable_metrics: bool = True

    # Celery
    celery_log_level: Annotated[str, StringConstraints(to_upper=True)] = "INFO"
    celery_log_file_path: str = "/tmp/celery.txt"
    celery_broker_url: str | None = None
    celery_result_backend_url: str | None = None

    @property
    def is_env_local_or_test(self) -> bool:
        return self.env in ("local", "test")


SETTINGS = Settings()