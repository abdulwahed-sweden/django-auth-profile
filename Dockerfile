FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/staticfiles && \
    chmod +x startup.sh && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["./startup.sh"]
