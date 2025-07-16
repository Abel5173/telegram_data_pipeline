from dagster import Definitions, load_assets_from_modules
from . import assets, jobs, schedules

defs = Definitions(
    assets=assets.all_assets,
    jobs=[jobs.telegram_pipeline_job],
    schedules=[schedules.daily_schedule],
)
