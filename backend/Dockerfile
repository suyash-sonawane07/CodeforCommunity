# ==============================================================================
# Stage 1: Build Next.js 14 Frontend
# ==============================================================================
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps || npm install

COPY frontend/ ./
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build
RUN cp -r .next/static .next/standalone/.next/

# ==============================================================================
# Stage 2: Unified Production Runner (Python 3.9 + Node.js)
# ==============================================================================
FROM python:3.9-slim

WORKDIR /code

# Install system dependencies, PostGIS client libraries, and Node.js runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl libpq-dev gcc postgresql-client \
 && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -y --no-install-recommends nodejs \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Install Python backend and AI layer dependencies
COPY backend/requirements.txt requirements.txt
COPY ai/requirements.txt ai-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r ai-requirements.txt

# Copy backend & AI code
COPY backend/ /code/
COPY ai/ /code/ai/

# Copy compiled frontend standalone from Stage 1
COPY --from=frontend-builder /app/frontend/.next/standalone /code/frontend/.next/standalone

ENV PYTHONPATH=/code
ENV PORT=8000
ENV BACKEND_URL=http://127.0.0.1:8000

EXPOSE 8000
CMD ["python", "scripts/start.py"]
