FROM python:3.12.9-slim

# Set working directory
WORKDIR /app

# Install necessary dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv .venv

# Activate the virtual environment and install dependencies
RUN .venv/bin/pip install --upgrade pip


# Copy application files
COPY . .

RUN .venv/bin/pip install -r requirements.txt

# Keep the container alive
CMD ["tail", "-f", "/dev/null"]