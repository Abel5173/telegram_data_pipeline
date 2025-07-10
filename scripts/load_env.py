from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
telegram_api_id = os.getenv("TELEGRAM_API_ID")
telegram_api_hash = os.getenv("TELEGRAM_API_HASH")
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT")

# Print variables to verify (for demonstration purposes)
print(f"Telegram API ID: {telegram_api_id}")
print(f"Telegram API Hash: {telegram_api_hash}")
print(f"Postgres User: {postgres_user}")
print(f"Postgres Password: {postgres_password}")
print(f"Postgres DB: {postgres_db}")
print(f"Postgres Host: {postgres_host}")
print(f"Postgres Port: {postgres_port}")
