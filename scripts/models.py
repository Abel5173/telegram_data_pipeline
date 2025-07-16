from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime

Base = declarative_base()

class FctMessage(Base):
    __tablename__ = "fct_messages"
    __table_args__ = {"schema": "marts"}

    message_id = Column(Integer, primary_key=True)
    channel_name = Column(String)
    message_text = Column(String)
    has_media = Column(Boolean)
    media_type = Column(String)
    media_path = Column(String)
    date_id = Column(Integer)
    channel_id = Column(Integer)

class ImageDetection(Base):
    __tablename__ = "image_detections"
    __table_args__ = {"schema": "raw"}

    message_id = Column(Integer, primary_key=True)
    channel_name = Column(String)
    product_label = Column(String)
    confidence = Column(Float)
