# Build stage for React Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Final stage for Python Backend + Static Frontend
FROM python:3.11-slim AS runner

WORKDIR /app

# Prevent Python from writing bytecode and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV ANONYMIZED_TELEMETRY=False

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and directory structure
COPY backend/ ./backend/

# Copy built frontend assets to frontend/dist so FastAPI serves them automatically
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose app port
EXPOSE 7860

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:7860/api/health || exit 1

# Launch FastAPI backend via Uvicorn
CMD ["sh", "-c", "uvicorn backend.api:app --host 0.0.0.0 --port ${PORT}"]
