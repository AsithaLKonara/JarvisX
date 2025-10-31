FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/ /app/backend/
COPY ../jarvis_llm_brain.py /app/
COPY ../core/ /app/core/
COPY ../utils/ /app/utils/
COPY ../speech/ /app/speech/
COPY ../system_monitor/ /app/system_monitor/
COPY ../memory/ /app/memory/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Expose port
EXPOSE 7860

# Start backend server
CMD ["python", "/app/backend/api.py"]

