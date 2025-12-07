## 🚀 Service Reliability Monitor
A high-performance, containerized service monitoring tool built using FastAPI and Python. It checks the health and version consistency of external services and provides proactive alerting on sustained failures.

## 🌟 Features Implemented
This solution meets all Core Requirements and implements key Stretch Goals for a robust, production-ready design:
* Core Monitoring Loop: Concurrent background checker running in a separate thread.
* Structured Logging: Uses Python's logging module for clean, streamable, categorized output (essential for Docker/CloudWatch).
* Stateful Alerting (Stretch Goal 3): Tracks consecutive failures and triggers a CRITICAL INCIDENT log message after 3 consecutive failures.
* Deployment Ready: Full support via Docker and Docker Compose for easy setup and configuration.
* ~~Operational Configuration: Monitoring interval is configurable via the MONITOR_INTERVAL_SECONDS environment variable (using Pydantic Settings).~~