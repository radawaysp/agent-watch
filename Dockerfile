FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src
COPY templates /app/templates
RUN python -m pip install --upgrade pip && python -m pip install .

WORKDIR /runtime
ENTRYPOINT ["agent-watch"]
