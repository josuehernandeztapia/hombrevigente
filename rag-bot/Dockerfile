FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-fly.txt .
RUN pip install --no-cache-dir -r requirements-fly.txt

COPY . .

RUN chmod +x scripts/docker_entrypoint.sh

ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

EXPOSE 8080

CMD ["scripts/docker_entrypoint.sh"]