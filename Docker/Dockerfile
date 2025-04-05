# Stage 1: Build dependencies
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

# Copy requirements and install dependencies
COPY requirements.txt /app/  
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache  # Clean up caches to reduce image size

# Stage 2: Final runtime image
FROM python:3.11-alpine

WORKDIR /app

# Install runtime libraries
RUN apk add --no-cache libffi

# Copy Python dependencies and application code from the builder stage
COPY --from=builder /usr/local /usr/local
COPY . /app/  

# Set environment variables
ENV PATH="/usr/local/bin:$PATH" \
    PYTHONPATH="/app/backend"

# Expose port
EXPOSE 5001

# Start the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5001"]