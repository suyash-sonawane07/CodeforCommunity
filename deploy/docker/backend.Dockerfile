FROM python:3.9-slim

WORKDIR /code

# PostGIS client libs are needed by psycopg2/geoalchemy runtime on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc postgresql-client \
 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt requirements.txt
COPY ai/requirements.txt ai-requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r ai-requirements.txt

COPY backend/ /code/
COPY ai/ /code/ai/

ENV PYTHONPATH=/code

EXPOSE 8000
CMD ["python", "scripts/start.py"]
