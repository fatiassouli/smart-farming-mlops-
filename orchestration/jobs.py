from dagster import define_asset_job, ScheduleDefinition
from .assets import raw_data, transformed_tables, data_quality_checks, mlflow_logging

# ═══════════════════════════════════════════════════════
# JOB : Pipeline complet (tous les assets)
# ═══════════════════════════════════════════════════════
full_pipeline_job = define_asset_job(
    name="full_pipeline",
    selection=[
        raw_data,
        transformed_tables,
        data_quality_checks,
        mlflow_logging,
    ],
    description="Pipeline complet Smart Farming : ingestion → dbt → qualité → MLflow"
)

# ═══════════════════════════════════════════════════════
# SCHEDULE : Exécution quotidienne à 2h du matin
# ═══════════════════════════════════════════════════════
daily_schedule = ScheduleDefinition(
    job=full_pipeline_job,
    cron_schedule="0 2 * * *",
    execution_timezone="Europe/Paris",
    name="daily_full_pipeline"
)
