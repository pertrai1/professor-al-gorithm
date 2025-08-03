# Multi-stage build for Professor Al Gorithm on Hugging Face Spaces
# Optimized for CPU Basic (free tier) - no GPU required
FROM python:3.9-slim

# Install Node.js and npm (optimized for smaller image size)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install backend dependencies 
COPY backend/package*.json backend/
RUN cd backend && npm ci && npm cache clean --force

# Copy backend source code
COPY backend/ backend/

# Build TypeScript code
RUN cd backend && npm run build

# Remove dev dependencies after build (keep image smaller)
RUN cd backend && npm prune --production

# Copy frontend files
COPY app.py .
COPY logo*.png ./
COPY README.md .

# Set environment variables for Hugging Face Spaces
ENV NODE_ENV=production
ENV PORT=3000
ENV GRADIO_SERVER_PORT=7860
ENV BACKEND_URL=http://localhost:3000

# Expose the port for Gradio
EXPOSE 7860

# Create startup script optimized for Hugging Face Spaces
RUN echo '#!/bin/bash\n\
echo "🎓 Starting Professor Al Gorithm on Hugging Face Spaces..."\n\
echo "📊 System info: $(uname -a)"\n\
echo "💾 Memory: $(free -h | head -2)"\n\
cd /app/backend && npm run start &\n\
BACKEND_PID=$!\n\
echo "⏳ Waiting for backend to start (PID: $BACKEND_PID)..."\n\
# Wait up to 30 seconds for backend to be ready\n\
for i in {1..30}; do\n\
  if curl -f http://localhost:3000/health >/dev/null 2>&1; then\n\
    echo "✅ Backend is ready after ${i} seconds"\n\
    break\n\
  fi\n\
  echo "⏳ Backend not ready yet, waiting... (attempt $i/30)"\n\
  sleep 1\n\
done\n\
echo "🔍 Final backend health check..."\n\
curl -f http://localhost:3000/health || echo "⚠️  Backend health check failed - continuing anyway"\n\
echo "🎨 Starting Gradio frontend on port 7860..."\n\
cd /app && python app.py' > /app/start.sh && chmod +x /app/start.sh

# Health check for container readiness
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# Start both backend and frontend
CMD ["/app/start.sh"]