# Simplified build for Professor Al Gorithm on Hugging Face Spaces
# Python-only version - no Node.js backend needed
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY logo*.png ./
COPY README.md .

# Set environment variables for Hugging Face Spaces
ENV GRADIO_SERVER_PORT=7860

# Expose the port for Gradio
EXPOSE 7860

# Health check removed - not needed for Hugging Face Spaces

# Start Gradio app directly
CMD ["python", "app.py"]