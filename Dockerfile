FROM python:3.11-slim AS base

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libnss3 libatk-bridge2.0-0 libgtk-3-0 libdrm2 libxkbcommon0 libasound2 \
      libgbm1 wget ca-certificates fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt && \
    playwright install --with-deps firefox

COPY src ./twitter_bookmarks_downloader

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "twitter_bookmarks_downloader.cli"]
CMD ["download-bookmarks", "--headless", "true"]

