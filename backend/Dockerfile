# Use Python 3.13 to match pyproject.toml requires-python
FROM python:3.13-slim

# Prevent Python from buffering stdout/stderr (useful for logs)
ARG INSTALL_DEBUGPY=false
# Pass --build-arg INSTALL_DEBUGPY=true to also install debugpy (for remote debugging)
# Keep this early so later layers can be cached separately for prod vs debug builds.
RUN if [ "$INSTALL_DEBUGPY" = "true" ]; then pip install --no-cache-dir debugpy; fi
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system build dependencies required for many Python packages
# Keep image small by cleaning apt lists after install
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libpq-dev \
       libssl-dev \
       libffi-dev \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel/setuptools which help build packages from pyproject
RUN python -m pip install --upgrade pip setuptools wheel

# Copy pyproject and optional lockfile first to leverage Docker layer caching.
# When pyproject.toml changes, dependency install is re-run; otherwise cached.
COPY pyproject.toml pyproject.lock* /app/

# Install project dependencies.
# For development editable install is convenient so changes picked up when source is mounted.
# If you prefer a non-editable install for production use `pip install --no-cache-dir .` instead.
RUN python -m pip install --no-cache-dir -e .

# Copy the rest of the application source
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Default command: run uvicorn in reload mode for dev. Remove --reload for production.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
