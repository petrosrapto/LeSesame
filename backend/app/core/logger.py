"""
Le Sésame Backend - Logging Configuration

Author: Petros Raptopoulos
Date: 2026/02/06
"""

import logging
import sys
from .config import settings

# Log format
LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s"

# Configure logging globally
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
    force=True
)

# Create logger for the app
logger = logging.getLogger("le_sesame")
logger.info(f"Logging initialized with level: {settings.log_level}")

# Reduce noise from external libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
