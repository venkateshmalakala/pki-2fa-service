# --- Stage 1: Builder ---
# We use a standard Python image to install dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
# Install dependencies into a specific folder so we can copy them later
RUN pip install --no-cache-dir -r requirements.txt

# --- Stage 2: Runtime ---
# We use a slim image for the final running container
FROM python:3.11-slim

# CRITICAL: Set Timezone to UTC
ENV TZ=UTC

WORKDIR /app

# Install system tools: Cron and Timezone data
RUN apt-get update && apt-get install -y \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Configure Timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy installed python libraries from Builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy our application code
COPY . .

# Setup the Cron Job
RUN echo "* * * * * cd /app && /usr/local/bin/python3 scripts/log_2fa_cron.py >> /cron/last_code.txt 2>&1" > /etc/cron.d/2fa-cron && chmod 0644 /etc/cron.d/2fa-cron
# 3. Apply the cron job
RUN crontab /etc/cron.d/2fa-cron
# 4. Create the /cron directory for logs
RUN mkdir -p /cron && chmod 755 /cron
# 5. Create the /data directory for the seed
RUN mkdir -p /data && chmod 755 /data

# Set Environment Variable for the App to use the volume
ENV SEED_PATH=/data/seed.txt

# Expose the API port
EXPOSE 8080

# START COMMAND
# We need to start BOTH Cron and the FastAPI server.
# This simple shell command does that.
CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080