# app/models.py
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime

# --- In-Memory Persistence ---
# Core Requirement 3: Store results persistently (in-memory dictionary for MVP)
LATEST_RESULTS: Dict[str, 'HealthResult'] = {}

# --- Configuration Model ---
# Core Requirement 1: Accept service configuration
class ServiceConfig(BaseModel):
    name: str
    url: str
    expected_version: Optional[str] = None
    group: str

# --- Result Model ---
# Core Requirement 2: Record status, latency, and version
class HealthResult(BaseModel):
    service_name: str
    timestamp: float = datetime.now().timestamp()
    status_code: int
    latency_ms: float
    version_found: Optional[str] = None
    is_available: bool
    version_match: bool