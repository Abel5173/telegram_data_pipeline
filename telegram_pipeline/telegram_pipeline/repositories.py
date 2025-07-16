from dagster import Definitions
from .jobs import telegram_pipeline_job
from .schedules import daily_schedule

defs = Definitions(
    jobs=[telegram_pipeline_job],
    schedules=[daily_schedule],
)
