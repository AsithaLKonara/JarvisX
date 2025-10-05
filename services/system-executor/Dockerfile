# JarvisX System Executor Dockerfile
FROM node:18-alpine

# Install system utilities
RUN apk add --no-cache \
    coreutils \
    procps \
    curl \
    wget \
    git \
    nano \
    vim

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S jarvisx -u 1001

# Change ownership
RUN chown -R jarvisx:nodejs /app
USER jarvisx

# Expose port
EXPOSE 8009

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8009/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the system executor service
CMD ["npm", "start"]
