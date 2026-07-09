from dagster import Definitions, load_assets_from_modules
from . import assets
from .jobs import full_pipeline_job, daily_schedule

# Charge automatiquement tous les @asset du module assets.py
all_assets = load_assets_from_modules([assets])

# Point d'entrée principal de Dagster
defs = Definitions(
    assets=all_assets,
    jobs=[full_pipeline_job],
    schedules=[daily_schedule],
)
