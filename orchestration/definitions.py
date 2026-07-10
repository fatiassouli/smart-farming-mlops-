from dagster import Definitions, load_assets_from_modules
from . import assets
from .jobs import (
    full_pipeline_job,
    ci_job,
    quality_job,
    daily_schedule,
    hourly_quality_schedule,
)

all_assets = load_assets_from_modules([assets])

defs = Definitions(
    assets=all_assets,
    jobs=[full_pipeline_job, ci_job, quality_job],
    schedules=[daily_schedule, hourly_quality_schedule],
)
