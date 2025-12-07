## 🚀 Service Reliability Monitor
A high-performance, containerized service monitoring tool built using FastAPI and Python. It checks the health and version consistency of external services and provides proactive alerting on sustained failures.

## 🌟 Features Implemented
This solution meets all Core Requirements and implements key Stretch Goals for a robust, production-ready design:
* Core Monitoring Loop: Concurrent background checker running in a separate thread.
* Structured Logging: Uses Python's logging module for clean, streamable, categorized output (essential for Docker/CloudWatch).
* Stateful Alerting: Tracks consecutive failures and triggers a CRITICAL INCIDENT log message after 3 consecutive failures.
* Version Drift Detection: Compares the expected version from configuration against the version found in the mock service response, logging a WARNING when drift occurs.
* Deployment Ready: Full support via Docker and Docker Compose for easy setup and configuration.

# 🛠️ Project Setup & Run
To install dependencies and run locally 
```bash
  pip install -r requirements.txt
  uvicorn app.main:app --reload --log-level info
```

To build and run the container using Docker Compose
```bash
docker compose up -d
```

# ☁️ Infrastructure Deployment Notes
### Configuration Management
The services.json file should be externalized and mounted via a ConfigMap (Kubernetes) or AWS S3 Volume.
The monitor should load it at startup using the CONFIG_FILE_PATH environment variable.

### State Persistence (KIV)
The in-memory Failure Count and LATEST_RESULTS must be replaced with a persistent, centralized store (e.g., AWS DynamoDB or Redis).
This guarantees state (alerts and health history) survives container restarts.

### Logging and Alerting
The structured output from the Python logging module should be streamed to a centralized logging system (e.g., AWS CloudWatch Logs).
CloudWatch Alarms or a dedicated alerting tool (like PagerDuty) must be configured to trigger when the log pattern "🚨 CRITICAL INCIDENT" is detected, indicating a sustained outage.
Warnings should be triggered on "⚠️ VERSION DRIFT ALERT".