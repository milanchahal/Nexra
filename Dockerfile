FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies (skip playwright install to save ~400MB)
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium || true

# Copy the application code
COPY . .

# Expose the port Railway will assign via $PORT
EXPOSE 8080

# Start the FastAPI app — Railway sets PORT env var automatically
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
