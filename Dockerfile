# Use Node.js 18 Alpine for smaller image size
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY backend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy backend source code
COPY backend/src ./src
COPY backend/tsconfig.json ./

# Install TypeScript and ts-node for production
RUN npm install -g typescript ts-node

# Build the TypeScript code
RUN npm run build

# Expose the port
EXPOSE 7860

# Set environment variables for Hugging Face Spaces
ENV NODE_ENV=production
ENV PORT=7860

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Start the server
CMD ["npm", "start"]