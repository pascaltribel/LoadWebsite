import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_engine import BaseDB 
from fetch_load_data import get_load_data 
from fetch_weather_data import get_belgium_weather
from models import Forecast, Data
from model import ForecastModel, ConvFeatureExtractor
import torch
import numpy as np

def predict(db, data):
    """Generates a prediction using the CNN"""
    if not data:
        return []
    timestamp = (datetime.datetime.fromisoformat(data['timestamp'][-1]) + datetime.timedelta(hours=31)).isoformat() ## +31 to respect the GMT+1
    
    model_y2 = torch.load("../torch/Forecaster.pt", weights_only=False).cpu()
    
    tensor_total_load = torch.tensor(np.array(data["total_load"], dtype=np.float32)).unsqueeze(0)
    tensor_total_load_1_year_before = torch.tensor(np.array(data["total_load_1_year_before"], dtype=np.float32)).unsqueeze(0)
    tensor_system_imbalance = torch.tensor(np.array(data["system_imbalance"], dtype=np.float32)).unsqueeze(0)
    features_load = torch.concatenate([tensor_total_load, tensor_total_load_1_year_before, tensor_system_imbalance], dim=0).unsqueeze(0)
    
    tensor_temperature = torch.tensor(np.array(data["temperature"], dtype=np.float32)).unsqueeze(0)
    tensor_precipitation = torch.tensor(np.array(data["precipitation"], dtype=np.float32)).unsqueeze(0)
    tensor_wind = torch.tensor(np.array(data["wind"], dtype=np.float32)).unsqueeze(0)
    tensor_pressure = torch.tensor(np.array(data["pressure"], dtype=np.float32)).unsqueeze(0)
    features_meteo = torch.concatenate([tensor_temperature, tensor_precipitation, tensor_wind, tensor_pressure], dim=0).unsqueeze(0)
    
    features_baseline = torch.tensor(np.array([data['total_load'][30-7*24]]))

    forecast = model_y2(features_load, features_meteo, features_baseline)

    timestamps = [timestamp]
    forecasts = [forecast]
    for timestamp, forecast_value in zip(timestamps, forecasts):
        existing_forecast = db.query(Forecast).filter(Forecast.timestamp == datetime.datetime.fromisoformat(timestamp)).first()

        if existing_forecast:
            existing_forecast.predicted_value = forecast_value
        else:
            new_forecast = Forecast(timestamp=datetime.datetime.fromisoformat(timestamp), predicted_value=forecast_value)
            db.add(new_forecast)
    
    db.commit()
    db.close()

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def store_historical_data(start_time, end_time):
    db = SessionLocal()

    current_time = start_time
    while current_time < end_time:
        print(current_time)
        weather_data = get_belgium_weather(end_time=current_time)
        load_data = get_load_data(end_time=current_time)

        data_entry = Data(
            timestamp=datetime.datetime.strptime(weather_data['timestamp'], "%Y-%m-%d %H:%M:%S"),
            total_load=load_data['total_load'],
            total_load_1_year_before=db.query(Data).where(Data.timestamp == current_time+datetime.timedelta(hours=-(24 * 365 + 30))).first().total_load,
            system_imbalance=load_data['system_imbalance'],
            temperature=weather_data['temperature'],
            precipitation=weather_data['precipitation'],
            wind=weather_data['wind'],
            pressure=weather_data['pressure'],
            elia=load_data['elia'],
        )

        db.add(data_entry)
        db.commit()
        current_time += datetime.timedelta(hours=1)
    
        last_entries = list(reversed(
    db.query(Data).order_by(Data.timestamp.desc()).limit(28*24).all()
        ))

        historical_data = [
            {"timestamp": entry.timestamp.isoformat(), 
            "total_load": entry.total_load,
            "total_load_1_year_before": entry.total_load_1_year_before,
            "system_imbalance": entry.system_imbalance,
            "temperature": entry.temperature,
            "precipitation": entry.precipitation,
            "wind": entry.wind,
            "pressure": entry.pressure,
            "elia": entry.elia}
            for entry in last_entries
        ]

        predict(SessionLocal(), {key: [entry[key] for entry in historical_data] for key in historical_data[0]})

    db.close()

if __name__ == "__main__":
    store_historical_data(start_time = datetime.datetime(2024, 5, 20, 15), end_time = datetime.datetime(2024, 5, 22, 0))
    store_historical_data(start_time = datetime.datetime(2024, 5, 22, 0), end_time = datetime.datetime(2025, 1, 1, 0))
