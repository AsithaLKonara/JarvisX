# JarvisX Personality Service Dockerfile
FROM node:18-alpine

# Install system dependencies for audio processing
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    ffmpeg \
    espeak \
    espeak-dev

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S jarvisx -u 1001

# Change ownership
RUN chown -R jarvisx:nodejs /app
USER jarvisx

# Expose port
EXPOSE 8007

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:8007/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start the personality service
CMD ["npm", "start"]
