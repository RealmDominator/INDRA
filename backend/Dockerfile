FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system indra && adduser --system --ingroup indra indra

COPY backend/requirements.runtime.txt /app/backend/requirements.runtime.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.runtime.txt

COPY backend /app/backend
COPY db /app/db
COPY scripts /app/scripts

RUN chown -R indra:indra /app
USER indra

ENV PYTHONPATH=/app/backend
EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
