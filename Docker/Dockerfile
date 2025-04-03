# Use a minimal base image
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install required system dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --user -r requirements.txt

# MultiBuild
FROM python:3.11-alpine

WORKDIR /app

# Install necessary libraries
RUN apk add --no-cache libffi

COPY --from=builder /root/.local /root/.local
COPY . /app/

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app"  

# Update to match FastAPI's port
EXPOSE 5001  

# Correct way to start Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
