# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
# Install dependencies to a temporary prefix
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder to /usr/local
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY utils/ ./utils/
COPY XanhSM-AI/ ./XanhSM-AI/

# Set PYTHONPATH to include /app for module discovery
ENV PYTHONPATH=/app

# Create a non-root user and set permissions for /app
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
