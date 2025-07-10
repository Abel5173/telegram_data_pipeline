from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, RPCError
from dotenv import load_dotenv
import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
import aiofiles
import pytz

# Load environment variables
load_dotenv()

# Configure logging to file and console
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler('logs/scrape.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

# Add both handlers to the logger
logger.handlers = []  # Clear any existing handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Telegram API credentials
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")
phone = os.getenv("TELEGRAM_PHONE")  # Optional: for first-time authentication

# Data lake directory
DATA_LAKE_PATH = "data/raw/telegram_messages"

# List of Telegram channels to scrape
CHANNELS = [
    "chemed123",
    "lobelia4cosmetics",
    "tikvahpharma"
]


async def scrape_channel(client, channel, start_date, end_date):
    """Scrape messages and images from a Telegram channel."""
    try:
        logger.info(f"Starting scrape for channel: {channel}")
        os.makedirs(DATA_LAKE_PATH, exist_ok=True)

        # Get channel entity
        entity = await client.get_entity(channel)

        # Create directory for channel
        channel_path = os.path.join(DATA_LAKE_PATH, channel)
        os.makedirs(channel_path, exist_ok=True)

        # Iterate over messages
        async for message in client.iter_messages(entity, limit=1000, offset_date=end_date):
            # Debug: Log message date
            logger.debug(f"Message {message.id} date: {message.date}")

            if message.date < start_date:
                logger.info(
                    f"Reached messages before {start_date} for {channel}, stopping.")
                break

            date_str = message.date.strftime("%Y-%m-%d")
            file_path = os.path.join(channel_path, f"{date_str}.json")

            # Prepare message data
            message_data = {
                "message_id": message.id,
                "date": message.date.isoformat(),
                "text": message.text,
                "has_media": bool(message.media),
                "media_type": None,
                "media_path": None
            }

            # Handle media (images)
            if message.photo:
                media_path = os.path.join(
                    channel_path, "images", f"{message.id}.jpg")
                os.makedirs(os.path.dirname(media_path), exist_ok=True)
                try:
                    await client.download_media(message, media_path)
                    message_data["media_type"] = "photo"
                    message_data["media_path"] = media_path
                    logger.info(
                        f"Downloaded image for message {message.id} in {channel}")
                except Exception as e:
                    logger.error(
                        f"Failed to download media for message {message.id}: {str(e)}")

            # Append to JSON file
            async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
                await f.write(json.dumps(message_data) + "\n")

            logger.info(f"Scraped message {message.id} from {channel}")

    except FloodWaitError as e:
        logger.warning(
            f"Rate limit hit for {channel}. Waiting {e.seconds} seconds.")
        await asyncio.sleep(e.seconds)
    except RPCError as e:
        logger.error(f"Telegram API error for {channel}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error for {channel}: {str(e)}")


async def main():
    """Main function to scrape multiple channels."""
    async with TelegramClient('session', api_id, api_hash) as client:
        # Optional: Authenticate if not already logged in
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input("Enter the code you received: ")
            await client.sign_in(phone, code)

        # Set timezone to UTC for consistency
        utc = pytz.UTC
        end_date = datetime.now(utc)
        start_date = end_date - timedelta(days=7)

        # Debug: Log start and end dates
        logger.debug(f"Scraping from {start_date} to {end_date}")

        for channel in CHANNELS:
            await scrape_channel(client, channel, start_date, end_date)

if __name__ == "__main__":
    asyncio.run(main())
