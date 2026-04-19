import os
import logging
from azure.monitor.opentelemetry import configure_azure_monitor

logger = logging.getLogger("brand-guardian-telemetry")

def setup_telemetry():
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.warning("No key foung, Telemetry is disabled")

    try:

        configure_azure_monitor(
            connection_string=connection_string,
            logger_name=logger
        )

        logger.info("Azure montior tracking enabled")

    except Exception as e:
        logger.error(f"failed to initialize azure monitor")

    