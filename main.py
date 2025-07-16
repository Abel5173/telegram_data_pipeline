from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from scripts.database import SessionLocal
from scripts.schemas import ProductStat, MessageSchema, ChannelActivitySchema
from scripts.crud import get_channel_activity, get_top_products, search_messages
import logging
from sqlalchemy import text
from fastapi import HTTPException


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Telegram Analytics API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/reports/top-products", response_model=list[ProductStat])
def top_products(limit: int = Query(10, gt=0, le=100), db: Session = Depends(get_db)):
    return get_top_products(db, limit)

@app.get("/api/search/messages", response_model=list[MessageSchema])
def messages_search(query: str, db: Session = Depends(get_db)):
    return search_messages(db, query)

@app.get("/api/channels/{channel_name}/activity", response_model=list[ChannelActivitySchema])
def channel_activity(channel_name: str, db: Session = Depends(get_db)):
    return get_channel_activity(db, channel_name)

@app.get("/channels/", response_model=list[str])
def get_channels(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT channel_name FROM public_marts.dim_channels"))
        channels = [row[0] for row in result]
        return channels
    except Exception as e:
        logger.exception("Channels query failed")
        raise HTTPException(status_code=500, detail="Channels query failed")
