from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class MessageSchema(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    has_media: bool
    media_type: str | None
    media_path: str | None


class TopProductSchema(BaseModel):
    product_label: str
    count: int

    class Config:
        from_attributes = True

class ChannelActivitySchema(BaseModel):
    date: str
    message_count: int

    class Config:
        from_attributes = True

class ProductStat(BaseModel):
    product_label: str
    mention_count: int

    class Config:
        from_attributes = True
