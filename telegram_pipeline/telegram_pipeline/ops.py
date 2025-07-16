from dagster import op
import subprocess

@op
def scrape_telegram_data():
    subprocess.run(["python", "scripts/scrape_telegram.py"], check=True)

@op
def load_raw_to_postgres():
    subprocess.run(["python", "scripts/load_to_postgres.py"], check=True)

@op
def run_dbt_transformations():
    subprocess.run(["dbt", "run"], cwd="path_to_your_dbt_project", check=True)

@op
def run_yolo_enrichment():
    subprocess.run(["python", "scripts/enrich_with_yolo.py"], check=True)
