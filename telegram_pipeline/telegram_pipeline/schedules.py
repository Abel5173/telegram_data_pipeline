from dagster import ScheduleDefinition
from .jobs import telegram_pipeline_job

daily_schedule = ScheduleDefinition(
    job=telegram_pipeline_job,
    cron_schedule="0 6 * * *",  
    name="daily_telegram_pipeline",
)
