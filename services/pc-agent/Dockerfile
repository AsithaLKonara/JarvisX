# JarvisX PC Agent Dockerfile
FROM node:18-alpine

# Install system dependencies for robotjs and screen capture
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    cairo-dev \
    jpeg-dev \
    pango-dev \
    musl-dev \
    giflib-dev \
    pixman-dev \
    pangomm-dev \
    libjpeg-turbo-dev \
    freetype-dev \
    xvfb \
    x11vnc \
    fluxbox \
    wget \
    chromium \
    chromium-chromedriver

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S jarvisx && \
    adduser -S jarvisx -u 1001

# Set permissions
RUN chown -R jarvisx:jarvisx /app

# Switch to non-root user
USER jarvisx

# Expose port
EXPOSE 8005

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8005/health || exit 1

# Start the application
CMD ["npm", "start"]
