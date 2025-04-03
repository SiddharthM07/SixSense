# Use a minimal base image
FROM python:3.11-alpine AS builder

WORKDIR /app

# Install required system dependencies
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev

# Copy requirements and install dependencies
COPY SixSense/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt  # Install globally

# MultiBuild
FROM python:3.11-alpine

WORKDIR /app

# Install necessary libraries
RUN apk add --no-cache libffi

COPY --from=builder /root/.local /root/.local
COPY . /app/  

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH="/app/SixSense"  

EXPOSE 5001  

CMD ["uvicorn", "SixSense.backend.main:app", "--host", "0.0.0.0", "--port", "5001", "--reload"]
