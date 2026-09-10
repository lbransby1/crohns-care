FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib \
    ANONYMIZED_TELEMETRY=False \
    HF_HOME=/home/appuser/.cache/hf

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /tmp/matplotlib /home/appuser/.cache \
    && chown -R appuser:appuser /app /tmp/matplotlib /home/appuser

USER appuser

# Warm the MiniLM ONNX weights so the first Railway request is not stalled.
RUN python -c "from chromadb.utils.embedding_functions import DefaultEmbeddingFunction; DefaultEmbeddingFunction()"

COPY --chown=appuser:appuser app ./app

EXPOSE 8000

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers
