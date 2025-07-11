import os
import json
import logging
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from ultralytics import YOLO
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/yolo_enrichment.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

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

# Load YOLOv8 model (pre-trained, suitable for e-commerce products)
model = YOLO('yolov8n.pt')  # Use yolov8n (nano) for lightweight detection


def create_image_detections_table(conn):
    """Create the raw.image_detections table if it doesn't exist."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE SCHEMA IF NOT EXISTS raw;
                CREATE TABLE IF NOT EXISTS raw.image_detections (
                    message_id BIGINT,
                    channel_name VARCHAR(255),
                    product_label VARCHAR(100),
                    confidence FLOAT,
                    bounding_box JSONB,
                    detection_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            logger.info("Created raw.image_detections table")
    except Exception as e:
        logger.error(f"Failed to create raw.image_detections table: {str(e)}")
        conn.rollback()
        raise


def enrich_images_with_yolo():
    """Run YOLOv8 on images and store detections in PostgreSQL."""
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        create_image_detections_table(conn)

        with conn.cursor() as cur:
            # Query messages with images
            cur.execute("""
                SELECT message_id, channel_name, media_path
                FROM raw.telegram_messages
                WHERE has_media = true AND media_type = 'photo' AND media_path IS NOT NULL;
            """)
            image_records = cur.fetchall()

            if not image_records:
                logger.warning("No images found in raw.telegram_messages")
                conn.close()
                return

            detections = []
            for message_id, channel_name, media_path in image_records:
                if not Path(media_path).exists():
                    logger.warning(f"Image not found: {media_path}")
                    continue

                try:
                    # Run YOLOv8 inference
                    results = model(media_path)
                    for result in results:
                        for box in result.boxes:
                            product_label = result.names[int(box.cls)]
                            confidence = float(box.conf)
                            bbox = {
                                'x': float(box.xyxy[0][0]),
                                'y': float(box.xyxy[0][1]),
                                'width': float(box.xyxy[0][2] - box.xyxy[0][0]),
                                'height': float(box.xyxy[0][3] - box.xyxy[0][1])
                            }
                            detections.append((
                                message_id,
                                channel_name,
                                product_label,
                                confidence,
                                json.dumps(bbox)
                            ))
                            logger.info(
                                f"Detected {product_label} in {media_path} with confidence {confidence}")
                except Exception as e:
                    logger.error(
                        f"Failed to process image {media_path}: {str(e)}")
                    continue

            if detections:
                # Bulk insert detections
                execute_values(
                    cur,
                    """
                    INSERT INTO raw.image_detections (
                        message_id, channel_name, product_label, confidence, bounding_box
                    ) VALUES %s
                    """,
                    detections
                )
                conn.commit()
                logger.info(
                    f"Inserted {len(detections)} detections into raw.image_detections")
            else:
                logger.warning("No detections to insert")

        conn.close()
        logger.info("Finished YOLO enrichment")

    except Exception as e:
        logger.error(f"Error during YOLO enrichment: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise


if __name__ == "__main__":
    enrich_images_with_yolo()
