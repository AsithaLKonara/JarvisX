FROM node:18-alpine

# Install Tesseract OCR and language packs
RUN apk add --no-cache \
    tesseract-ocr \
    tesseract-ocr-data-sin \
    tesseract-ocr-data-eng \
    tesseract-ocr-data-script-latn \
    tesseract-ocr-data-script-sinh

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

# Expose port
EXPOSE 8011

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8011/health || exit 1

# Start the service
CMD ["npm", "start"]
