# IMPORTANT : ce Dockerfile doit être buildé avec la RACINE DU REPO comme contexte
# (et non backend/), car le service importe mlops/model_loader.py et models/.
#
# Depuis la racine du projet :
#   docker build -f backend/Dockerfile -t smart-farming-api .
#   docker run -p 8000:8000 -v $(pwd)/mlruns:/app/mlruns smart-farming-api

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# On copie le backend, mlops/ (import mlops.model_loader) et les modèles .pkl
COPY backend/ ./backend/
COPY mlops/ ./mlops/
COPY models/ ./models/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8000"]