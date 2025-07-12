# Telegram Medical Businesses Data Platform

## Overview

This project is an end-to-end data platform designed to generate insights about Ethiopian medical businesses from public Telegram channels. It leverages modern data engineering tools and best practices, including:

- **Data extraction from Telegram** using Telethon.
- **Data lake organization** for raw data storage.
- **Data warehouse (PostgreSQL)** with a dimensional star schema.
- **Data transformation and modeling** using dbt.
- **Data enrichment** with object detection on images using YOLOv8.
- **Analytical API exposure** using FastAPI.
- **Pipeline orchestration** with Dagster.
- **Reproducible, containerized environment** via Docker.

## Business Questions Answered

- What are the top 10 most frequently mentioned medical products or drugs across all channels?
- How does the price or availability of a specific product vary across different channels?
- Which channels have the most visual content (e.g., images of pills vs. creams)?
- What are the daily and weekly trends in posting volume for health-related topics?

---

## Project Structure

```
.
├── data/
│   └── raw/
│       └── telegram_messages/
│           └── YYYY-MMDD/
│               └── channel_name.json
├── dbt/
│   └── my_project/
│       ├── models/
│       │   ├── staging/
│       │   ├── marts/
│       │   └── ...
│       └── ...
├── dags/                 # Dagster pipelines
├── src/
│   ├── scraping/         # Telegram data scraping scripts
│   ├── enrichment/       # YOLOv8 image detection scripts
│   └── api/              # FastAPI application
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                  # Environment variables (NOT in version control)
├── .gitignore
└── README.md
```

---

## Getting Started

### 0. Project Setup & Environment Management

#### Prerequisites

- Docker & Docker Compose
- Python 3.9+
- Git

#### 1. Clone the Repository

```bash
git clone <repo-url>
cd <repo-directory>
```

#### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your secrets (Telegram API credentials, database passwords, etc.):

```bash
cp .env.example .env
```

**Never commit your `.env` file!** It's included in `.gitignore`.

#### 3. Build and Run the Project

```bash
docker-compose up --build
```

This will start:
- A PostgreSQL database
- The Python application (for scraping, enrichment, and API)
- Dagster for orchestration

#### 4. Install Python Dependencies (if running locally)

```bash
pip install -r requirements.txt
```

---

## 1. Data Scraping and Collection

- **Scrapers** located in `src/scraping/` extract messages and images from Telegram channels such as:
    - [Chemed Telegram Channel](https://t.me/lobelia4cosmetics)
    - [Tikvah Pharma](https://t.me/tikvahpharma)
    - More from [et.tgstat.com/medicine](https://et.tgstat.com/medicine)

- **Raw Data Storage:**  
  Raw JSON files are saved in a partitioned structure under `data/raw/telegram_messages/YYYY-MMDD/channel_name.json`.

- **Logging:**  
  All scraping activities and errors are logged for traceability.

---

## 2. Data Modeling and Transformation (with dbt)

- **Load:**  
  A loader script ingests raw JSON into a `raw` schema in the PostgreSQL warehouse.

- **dbt Project:**  
  Located in `dbt/my_project/`. Set up by running:
  ```bash
  dbt init my_project
  ```

- **Models:**
    - **Staging models:** Clean and restructure the raw data (`stg_telegram_messages.sql`).
    - **Data Marts:** Star schema with:
        - `dim_channels`: Telegram channel metadata
        - `dim_dates`: Time dimension for analysis
        - `fct_messages`: Fact table with metrics per message

- **Testing & Documentation:**  
  - Use dbt's built-in and custom tests.
  - Run `dbt docs generate` and `dbt docs serve` for documentation.

---

## 3. Data Enrichment with YOLOv8

- **Image Detection:**  
  Scripts in `src/enrichment/` scan new images and apply a YOLOv8 model (via `ultralytics` package).

- **Integration:**  
  Detection results are loaded into a new fact table (`fct_image_detections`) with columns:
    - `message_id` (foreign key to `fct_messages`)
    - `detected_object_class`
    - `confidence_score`

---

## 4. Analytical API (FastAPI)

- **Endpoints** expose clean, analytical views (e.g., top products, trends, channel statistics) from the data warehouse.
- Located in `src/api/`.
- Run locally (for development):
  ```bash
  uvicorn src.api.main:app --reload
  ```

---

## 5. Pipeline Orchestration (Dagster)

- All ETL/ELT tasks are orchestrated with Dagster (`dags/`).
- Pipelines cover scraping, loading, transformation, enrichment, and API update tasks.

---

## Testing & Validation

- Data quality is enforced via dbt tests and logging.
- Pipeline tasks are monitored and retried by Dagster.

---

## Managing Secrets

All credentials (Telegram API keys, DB passwords, etc.) are managed via environment variables and `.env` file.  
**Never commit secrets to version control!**

---

## Key Dependencies

- [Telethon](https://github.com/LonamiWebs/Telethon) (Telegram scraping)
- [dbt](https://www.getdbt.com/)
- [ultralytics](https://github.com/ultralytics/ultralytics) (YOLOv8)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Dagster](https://dagster.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to your branch
5. Open a pull request

---

## Documentation

- Data model and pipeline architecture are documented in the `docs/` directory and via dbt docs.
- For questions, join the #all-week7 Slack channel.

---

## Authors

- Kara Solutions Data Engineering Team ; ) LOL