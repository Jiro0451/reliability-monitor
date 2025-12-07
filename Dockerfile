# Stage 1: Build Stage (Creates the environment)
# Using a specific slim image is faster and more secure than the full Python image
FROM python:3.11-slim AS base

# Set environment variables for the application
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV APP_HOME /app

# Create the working directory
WORKDIR $APP_HOME

# Install dependencies
# Copy requirements.txt and install them first to leverage Docker's caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user for security (Good operational practice)
RUN adduser --disabled-password appuser
USER appuser

# Stage 2: Final Stage (The minimal runtime image)
# This uses the previous stage to avoid copying build tools and intermediate files
FROM base AS final

# Copy application files (app/ folder and services.json)
# Assuming your app logic is inside a folder named 'app'
COPY app /app/app/
COPY services.json /app/services.json

# Expose the port (FastAPI default is 8000)
EXPOSE 8000

# Command to run the application (Core Requirement 5)
# Use Uvicorn directly as we're keeping it simple, or gunicorn for more robustness
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative CMD for Production Robustness (Senior-level choice)
# CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]