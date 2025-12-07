# app/checker.py
import random
import logging
from datetime import datetime
from typing import List, Dict
from time import sleep


from app.models import ServiceConfig, HealthResult, LATEST_RESULTS

logger = logging.getLogger("checker")
ALERT_THRESHOLD = 3 # Define 3 consecutive failures as an incident trigger
FAILURE_COUNT: Dict[str, int] = {} # In-memory tracker for consecutive fails

# --- Configuration Loader ---
def load_services_config(file_path: str = "services.json") -> List[ServiceConfig]:
    """Loads and validates service configurations from a JSON file."""
    # In a real app, this uses 'json.load'
    # For now, we'll assume the external code (main.py) handles the load
    # and passes in the list of Pydantic objects.
    pass


# --- Core Requirement 2: The Pinger (Simulated) ---
def check_service(config: ServiceConfig) -> HealthResult:
    """Performs a simulated health check and returns the result."""

    # 1. Simulate Latency (50ms to 500ms)
    latency_ms = round(random.uniform(50.0, 500.0), 2)

    # 2. Simulate Status Code (80% success, 20% failure)
    status_code = 200 if random.random() < 0.4 else 503

    # 3. Simulate Version Found and Version Drift (Stretch Goal 1)
    version_found = config.expected_version
    version_match = True

    if config.expected_version and random.random() < 0.2:
        # Simulate a mismatched version 20% of the time
        version_found = config.expected_version + ".drift"
        version_match = False

    # 4. Calculate Availability
    is_available = status_code < 400

    return HealthResult(
        service_name=config.name,
        status_code=status_code,
        latency_ms=latency_ms,
        version_found=version_found,
        is_available=is_available,
        version_match=version_match
    )


# --- Scheduler/Worker Loop (Core Requirement 2 & 3) ---
def start_checker_loop(configs: List[ServiceConfig], interval_seconds: int = 60):
    """The main worker thread that periodically checks all services."""
    logger.info(f"Starting service checker loop, checking every {interval_seconds} seconds...")

    while True:
        for config in configs:
            try:
                result = check_service(config)
                service_name = config.name

                # --- Alerting and Failure Counting Logic ---
                if result.is_available:
                    # Case 1: Service is healthy
                    if FAILURE_COUNT.get(service_name, 0) > 0:
                        # Log recovery only if it was previously alerting
                        if FAILURE_COUNT[service_name] >= ALERT_THRESHOLD:
                            logger.warning(
                                f"✅ RECOVERY: {service_name} recovered after "
                                f"{FAILURE_COUNT[service_name]} consecutive failures."
                            )
                        # Reset the counter
                        FAILURE_COUNT[service_name] = 0
                else:
                    # Case 2: Service failed, increment counter
                    FAILURE_COUNT[service_name] = FAILURE_COUNT.get(service_name, 0) + 1
                    current_count = FAILURE_COUNT[service_name]

                    if current_count == ALERT_THRESHOLD:
                        # 🚨 CRITICAL ALERT TRIGGER 🚨
                        # Log as ERROR for max visibility in logs/Docker stream
                        logger.error(
                            f"🚨 CRITICAL INCIDENT: {service_name} has failed "
                            f"{ALERT_THRESHOLD} consecutive times! Status={result.status_code}. "
                            f"Immediate attention required."
                        )
                    elif current_count > ALERT_THRESHOLD:
                        # Log continued failure at a lower level to prevent alert spam
                        logger.error(f"🚨 Continuing INCIDENT: {service_name} still DOWN (Count: {current_count}).")

                # Core Requirement 3: Store result in our in-memory cache
                LATEST_RESULTS[config.name] = result

                logger.info(
                    f"Checked {config.name}: Status={result.status_code}, Latency={result.latency_ms}ms, "
                    f"Available={result.is_available}, VersionMatch={result.version_match}"
                )


            except Exception as e:
                logger.error(f"Error checking {config.name}: An exception occurred.", exc_info=True)

        sleep(interval_seconds)