FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY utils/ ./utils/
COPY models/ ./artifacts/

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "app/app.py"]