FROM node:18-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    festival \
    festvox-kallpc16k \
    espeak \
    espeak-data \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Create temp directory for audio files
RUN mkdir -p /tmp

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["node", "main.js"]
