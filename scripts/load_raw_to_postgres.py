import os
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from pathlib import Path

# Configure logging to file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/load_raw.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger.handlers = []
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Load environment variables
load_dotenv()

# PostgreSQL connection parameters
db_params = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT')
}

# Data lake path
DATA_LAKE_PATH = "../data/raw/telegram_messages"


def create_raw_table(conn):
    """Create the raw.telegram_messages table if it doesn't exist."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE SCHEMA IF NOT EXISTS raw;
                CREATE TABLE IF NOT EXISTS raw.telegram_messages (
                    message_id BIGINT,
                    channel_name VARCHAR(255),
                    date TIMESTAMP WITH TIME ZONE,
                    text TEXT,
                    has_media BOOLEAN,
                    media_type VARCHAR(50),
                    media_path VARCHAR(512),
                    raw_data JSONB
                );
            """)
            conn.commit()
            logger.info("Created raw.telegram_messages table")
    except Exception as e:
        logger.error(f"Failed to create raw.telegram_messages table: {str(e)}")
        conn.rollback()
        raise


def load_json_to_postgres():
    """Load JSON files from data lake into PostgreSQL."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        create_raw_table(conn)

        with conn.cursor() as cur:
            for channel_dir in Path(DATA_LAKE_PATH).iterdir():
                if not channel_dir.is_dir():
                    continue
                channel_name = channel_dir.name
                logger.info(f"Processing channel: {channel_name}")

                for json_file in channel_dir.glob("*.json"):
                    logger.info(f"Loading file: {json_file}")
                    with open(json_file, 'r', encoding='utf-8') as f:
                        messages = [json.loads(line) for line in f if line.strip()]

                    if not messages:
                        logger.warning(f"No data in {json_file}")
                        continue

                    # Prepare data for bulk insert
                    values = [
                        (
                            msg['message_id'],
                            channel_name,
                            msg['date'],
                            msg['text'],
                            msg['has_media'],
                            msg['media_type'],
                            msg['media_path'],
                            json.dumps(msg)
                        )
                        for msg in messages
                    ]

                    # Bulk insert
                    execute_values(
                        cur,
                        """
                        INSERT INTO raw.telegram_messages (message_id, channel_name, date, text, has_media, media_type, media_path, raw_data) VALUES %s
                        """,
                        values
                    )
                    conn.commit()
                    logger.info(f"Loaded {len(values)} messages from {json_file}")

        conn.close()
        logger.info("Finished loading data to PostgreSQL")

    except Exception as e:
        logger.error(f"Error loading data to PostgreSQL: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise


if __name__ == "__main__":
    load_json_to_postgres()
