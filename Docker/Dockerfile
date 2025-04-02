# Use a minimal base image
FROM python:3.11-slim AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --user -r requirements.txt

# Start final stage
FROM python:3.11-slim

WORKDIR /app

# Copy only necessary files from builder stage
COPY --from=builder /root/.local /root/.local
COPY . /app/

# Ensure the Python binary uses the installed packages
ENV PATH="/root/.local/bin:$PATH"

EXPOSE 5000

CMD ["python", "backend/main.py"]
