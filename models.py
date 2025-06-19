from sqlalchemy import Column, Integer, Float, DateTime
from database_engine import BaseDB
from datetime import datetime

class Data(BaseDB):
    __tablename__ = "database"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_load = Column(Float)
    total_load_1_year_before = Column(Float)
    system_imbalance = Column(Float)
    temperature = Column(Float)
    precipitation = Column(Float)
    wind = Column(Float)
    pressure = Column(Float)
    elia = Column(Float)

class Forecast(BaseDB):
    __tablename__ = "forecast"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, unique=True, nullable=False)
    predicted_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
