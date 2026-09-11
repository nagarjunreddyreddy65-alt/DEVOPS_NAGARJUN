# Container definition for Autonomous DevOps CI/CD Experimentation
FROM python:3.11-slim

WORKDIR /workspace

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application and source tree
COPY . .

# Default entrypoint runs tests and validates prediction pipeline
CMD ["pytest", "-v", "tests/"]
