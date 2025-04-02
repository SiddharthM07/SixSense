# Use a minimal base image
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install required system dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Start final stage
FROM python:3.11-alpine

WORKDIR /app

# Install runtime dependencies
RUN apk add --no-cache libffi

# Copy only necessary files from builder stage
COPY --from=builder /usr/lib/python3.11/site-packages /usr/lib/python3.11/site-packages
COPY --from=builder /usr/bin/python3 /usr/bin/python3
COPY . /app/

# Clean up build dependencies to save space
RUN apk del gcc musl-dev python3-dev libffi-dev

# Ensure the Python binary uses the installed packages
ENV PATH="/usr/bin:$PATH"

EXPOSE 5000

CMD ["python3", "backend/main.py"]

