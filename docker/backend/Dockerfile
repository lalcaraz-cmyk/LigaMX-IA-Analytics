# Use a slim Python 3.13 base image for a small and reliable runtime.
FROM python:3.13-slim

# Prevent Python from writing .pyc files and ensure unbuffered output.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install only the system packages needed for building Python dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv as the package manager.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
RUN uv --version

# Set the working directory for the application.
WORKDIR /app

# Copy dependency metadata first to maximize Docker layer caching.
COPY backend/pyproject.toml ./pyproject.toml
COPY README.md ./README.md

# Install project dependencies into the virtual environment.
RUN uv sync --no-dev --no-install-project

# Copy the application source after dependencies are installed.
COPY backend/ ./

# Expose the FastAPI development port.
EXPOSE 8000

# Run the FastAPI app with live reloading.
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
