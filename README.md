Amharic E-commerce Data Extractor
Overview
This project consolidates Telegram e-commerce data for EthioMart, extracting and transforming data from Telegram channels (chemed123, lobelia4cosmetics, tikvahpharma) into a star schema for analytical purposes.
Tasks
Task 2: Data Transformation

Objective: Load raw JSON data into PostgreSQL and transform it into a star schema using dbt.
Process:
Scraped messages and images into data/raw/telegram_messages.
Loaded data into raw.telegram_messages using load_raw_to_postgres.py.
Created dbt models: staging.stg_telegram_messages, marts.dim_channels, marts.dim_dates, marts.fct_messages.
Added tests (unique, not_null, unique_combination_of_columns) in schema.yml.
Generated documentation with dbt docs generate.


Output: Star schema in staging and marts schemas, with ~1980 messages in marts.fct_messages.

Task 3: Data Enrichment with YOLO

Objective: Enrich Telegram message data by detecting products in images using YOLOv8.
Process:
Installed ultralytics for YOLOv8.
Created enrich_with_yolo.py to process images from raw.telegram_messages.media_path, storing detections in raw.image_detections.
Fixed duplicate source definition error by consolidating sources in models/staging/sources.yml.
Fixed POSTGRES_HOST error by ensuring .env includes all required variables.
Fixed missing raw.telegram_messages by reloading data.
Fixed missing raw.image_detections by rerunning enrich_with_yolo.py.
Fixed missing tikvahpharma images by redownloading with scrape_telegram.py.
Fixed schema prefixing by removing schema from profiles.yml.
Updated marts.fct_messages to include product_label via a LEFT JOIN with raw.image_detections.
Added accepted_values test for product_label in schema.yml.
Extended data extraction to 30 days for ~2028 messages and ~406 images.


Output: raw.image_detections with ~406 detections, marts.fct_messages enriched with product labels.

Directory Structure
telegram_data_pipeline/
├── data/
│   └── raw/telegram_messages/
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_telegram_messages.sql
│   │   │   ├── sources.yml
│   │   │   └── schema.yml
│   │   ├── marts/
│   │   │   ├── dim_channels.sql
│   │   │   ├── dim_dates.sql
│   │   │   ├── fct_messages.sql
│   │   │   └── schema.yml
│   ├── profiles.yml
│   └── dbt_project.yml
├── scripts/
│   ├── scrape_telegram.py
│   ├── load_raw_to_postgres.py
│   ├── enrich_with_yolo.py
│   └── run_dbt.py
├── logs/
├── .env
├── .gitignore
└── README.md

Future Work

Task 4: Build a FastAPI endpoint to query the star schema.
Task 5: Develop a Streamlit dashboard for business insights (e.g., top products).
