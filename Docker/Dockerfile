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


RUN apk add --no-cache libffi


COPY --from=builder /root/.local /root/.local
COPY . /app/


ENV PATH="/root/.local/bin:$PATH"

EXPOSE 5000

CMD ["python", "backend/main.py"]
