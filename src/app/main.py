import logging

import uvicorn

from app.create_app import create_app
from app.env import SETTINGS

# Create app
app = create_app()

if __name__ == "__main__":
    # Start server
    logging.info(f"Server Log Level: {SETTINGS.server_log_level}")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=SETTINGS.server_port,
        log_level=SETTINGS.server_log_level,
        reload=True if SETTINGS.is_env_local_or_test else False,
    )
