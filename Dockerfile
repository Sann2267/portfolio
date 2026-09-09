# Production image: gunicorn serving the Flask app as a non-root user.
# Build:  docker build -t case-room .
# Run:    docker run --rm -p 8000:8000 -e SECRET_KEY=... -e SITE_URL=https://example.com case-room
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py wsgi.py pyproject.toml ./
COPY app ./app
COPY templates ./templates
COPY static ./static
COPY content ./content

RUN useradd --system --uid 10001 --no-create-home portfolio \
    && chown -R portfolio:portfolio /app
USER portfolio

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2).status == 200 else 1)"

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "wsgi:app"]
