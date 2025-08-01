# Multi-stage build for Professor Al Gorithm on Hugging Face Spaces
FROM python:3.9-slim

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install backend dependencies
COPY backend/package*.json backend/
RUN cd backend && npm ci --only=production

# Install TypeScript and ts-node globally
RUN npm install -g typescript ts-node

# Copy backend source code
COPY backend/ backend/

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

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🎓 Starting Professor Al Gorithm..."\n\
cd /app/backend && npm run start &\n\
echo "⏳ Waiting for backend to start..."\n\
sleep 10\n\
echo "🎨 Starting Gradio frontend..."\n\
cd /app && python app.py' > /app/start.sh && chmod +x /app/start.sh

# Start both backend and frontend
CMD ["/app/start.sh"]