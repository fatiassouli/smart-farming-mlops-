from dagster import define_asset_job, DefaultScheduleDefinition
from .assets import (
    unit_tests, code_quality, security_scan,
    raw_data, transformed_tables,
    data_quality_checks, data_drift_check,
    mlflow_logging,
    api_integration_test, performance_test
)

# Job complet (tout le pipeline)
full_pipeline_job = define_asset_job(
    name="full_pipeline",
    selection=[
        unit_tests, code_quality, security_scan,
        raw_data, transformed_tables,
        data_quality_checks, data_drift_check,
        mlflow_logging,
        api_integration_test, performance_test
    ],
    description="Pipeline complet avec tous les tests"
)

# Job CI rapide (tests + qualité, sans ingestion lourde)
ci_job = define_asset_job(
    name="ci_pipeline",
    selection=[unit_tests, code_quality, security_scan, data_quality_checks],
    description="Pipeline CI rapide (tests + qualité)"
)

# Job qualité seulement
quality_job = define_asset_job(
    name="quality_check",
    selection=[data_quality_checks, data_drift_check],
    description="Validation qualité et drift uniquement"
)

# Schedules
daily_schedule = DefaultScheduleDefinition(
    job=full_pipeline_job,
    cron_schedule="0 2 * * *",
    execution_timezone="Europe/Paris",
    name="daily_full_pipeline"
)

hourly_quality_schedule = DefaultScheduleDefinition(
    job=quality_job,
    cron_schedule="0 * * * *",
    execution_timezone="Europe/Paris",
    name="hourly_quality_check"
)
