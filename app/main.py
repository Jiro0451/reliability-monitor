import json
import threading
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import Field
from pydantic.v1 import BaseSettings

# Import the core logic and models
from app.models import ServiceConfig, HealthResult, LATEST_RESULTS
from app.checker import start_checker_loop

# --- Logging Setup ---
# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("main") # Create logger instance for this module

# Pydantic Settings reads from environment variables first, then uses defaults
class Settings(BaseSettings):
    # Reads from env var CONFIG_FILE_PATH, defaults to 'services.json'
    CONFIG_FILE_PATH: str = "services.json"
    # Reads from env var MONITOR_INTERVAL_SECONDS, defaults to 10
    MONITOR_INTERVAL_SECONDS: int = 2

SETTINGS = Settings() # Load settings object
BASE_DIR = Path(__file__).resolve().parent.parent # Project root for robust path finding

# --- Configuration Loader ---
def load_configs() -> List[ServiceConfig]:
    """Loads and validates service configurations from the JSON file."""
    # Use BASE_DIR for reliable path resolution (Fixes common file-not-found issue)
    full_path = BASE_DIR / SETTINGS.CONFIG_FILE_PATH

    try:
        with open(full_path, 'r') as f:
            data = json.load(f)
        return [ServiceConfig(**item) for item in data]
    except FileNotFoundError:
        logger.error(f"Configuration file not found at {full_path}")
        return []
    except Exception as e:
        logger.error(f"Failed to load or validate configuration: {e}", exc_info=True)
        return []

# --- FastAPI App Setup ---

app = FastAPI(title="Service Reliability Monitor")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Event triggered on startup and shutdown (replaces on_event)."""

    # --- STARTUP LOGIC ---
    logger.info(f"Application starting up with interval: {SETTINGS.MONITOR_INTERVAL_SECONDS}s")

    configs = load_configs()
    if configs:
        logger.info(f"Loaded {len(configs)} services. Initializing monitoring worker...")

        checker_thread = threading.Thread(
            target=start_checker_loop,
            args=(configs, SETTINGS.MONITOR_INTERVAL_SECONDS),  # Use settings value
            daemon=True
        )
        checker_thread.start()
    else:
        logger.warning("No services configured. Monitoring functionality is disabled.")

    yield  # This line signals the application is ready to handle requests

    # --- SHUTDOWN LOGIC (Future-proofing for graceful exit) ---
    # When the server shuts down, the code below 'yield' runs.
    logger.info("Application shutting down. Waiting for background tasks...")
    # Add graceful shutdown logic here later (e.g., stopping the checker thread)


app = FastAPI(title="Service Reliability Monitor", lifespan=lifespan)


# --- API Endpoint (No Change Needed) ---
@app.get("/api/v1/health", response_model=List[HealthResult])
async def get_latest_health():
    """Returns the latest health check result for every monitored service."""
    # Convert the dictionary values into a list to return
    if not LATEST_RESULTS:
        raise HTTPException(status_code=404, detail="No health check results available yet.")

    return list(LATEST_RESULTS.values())