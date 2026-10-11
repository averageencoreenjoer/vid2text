FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VID2TEXT_ROOTS=/data \
    VID2TEXT_INPUT=/data/input \
    VID2TEXT_OUTPUT=/data/output \
    VID2TEXT_MODEL_DIR=/models

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install .

RUN mkdir -p /data/input /data/output /models
EXPOSE 8000

ENTRYPOINT ["vid2text"]
CMD ["serve", "--host", "0.0.0.0", "--no-browser"]
