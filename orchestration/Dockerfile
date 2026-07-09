# Dockerfile pour l'orchestration Dagster
# Build depuis la racine du repo : docker build -f orchestration/Dockerfile .

FROM python:3.11-slim

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer dbt + dépendances Python
RUN pip install --no-cache-dir \
    dagster==1.7.* \
    dagster-webserver==1.7.* \
    dbt-duckdb==1.7.* \
    pandas \
    pyyaml \
    scikit-learn \
    mlflow==2.14.* \
    joblib

# Copier le code de l'orchestration
COPY orchestration/ ./orchestration/

# Copier les dépendances des autres modules (montés en volume en prod)
COPY dataops/ ./dataops/
COPY transform/ ./transform/
COPY data_quality/ ./data_quality/
COPY mlops/ ./mlops/

# Créer le home Dagster
ENV DAGSTER_HOME=/opt/dagster/dagster_home
RUN mkdir -p $DAGSTER_HOME

EXPOSE 3000
