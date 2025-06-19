from csv_to_db import *
import threading
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
    timestamp = (datetime.datetime.fromisoformat(data['timestamp'][-1]) + datetime.timedelta(hours=31)).isoformat()

    model = torch.load("../torch/Forecaster.pt", weights_only=False).cpu()
    
    tensor_total_load = torch.tensor(np.array(data["total_load"], dtype=np.float32)).unsqueeze(0)
    tensor_total_load_1_year_before = torch.tensor(np.array(data["total_load_1_year_before"], dtype=np.float32)).unsqueeze(0)
    tensor_system_imbalance = torch.tensor(np.array(data["system_imbalance"], dtype=np.float32)).unsqueeze(0)
    features_load = torch.concatenate([tensor_total_load, tensor_total_load_1_year_before, tensor_system_imbalance], dim=0).unsqueeze(0)
    
    tensor_temperature = torch.tensor(np.array(data["temperature"], dtype=np.float32)).unsqueeze(0)
    tensor_precipitation = torch.tensor(np.array(data["precipitation"], dtype=np.float32)).unsqueeze(0)
    tensor_wind = torch.tensor(np.array(data["wind"], dtype=np.float32)).unsqueeze(0)
    tensor_pressure = torch.tensor(np.array(data["pressure"], dtype=np.float32)).unsqueeze(0)
    features_meteo = torch.concatenate([tensor_temperature, tensor_precipitation, tensor_wind, tensor_pressure], dim=0).unsqueeze(0)
    
    features_baseline = torch.tensor(np.array([data['total_load'][-7*24+30]], dtype=np.float32))
    with torch.no_grad():
        forecast = model(features_load.to("cpu"), features_meteo.to("cpu"), features_baseline.to("cpu")).cpu()

    new_forecast = Forecast(timestamp=datetime.datetime.fromisoformat(timestamp), predicted_value=forecast)
    db.add(new_forecast)
    db.commit()
    db.close()

start_index = 30001
interval = 0.2

def insert_periodically():
    global start_index

    row = data.iloc[start_index]
    entry_data = {correspondances[key]: row[key] for key in correspondances}

    insert_entry(
        db=SessionLocal(),
        timestamp=datetime.datetime.strptime(entry_data['timestamp'], "%Y-%m-%d %H:%M:%S+00:00"),
        total_load=entry_data['total_load'],
        total_load_1_year_before=entry_data['total_load_1_year_before'],
        system_imbalance=entry_data['system_imbalance'],
        temperature=entry_data['temperature'],
        precipitation=entry_data['precipitation'],
        wind=entry_data['wind'],
        pressure=entry_data['pressure'],
        elia=entry_data['elia']
    )

    db = SessionLocal()
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
    #print(historical_data[-1])
    start_index += 1
    threading.Timer(interval, insert_periodically).start()

# Démarrer la boucle périodique
insert_periodically()
