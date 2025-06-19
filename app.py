from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import asc
from sqlalchemy.orm import Session, aliased
from database_engine import SessionLocal
from models import Data, Forecast
import numpy as np
import pandas as pd
from model import *

app = Flask(__name__)
CORS(app)


@app.route("/data", methods=["GET"])
def get_data():
    """Fetch last 24*28 records and return stored predictions"""
    db: Session = SessionLocal()
    
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

    stored_predictions = db.query(Forecast).order_by(Forecast.timestamp.desc()).limit(28*24+31).all()[::-1]
    db.close()
    
    if stored_predictions == []:
        predictions = [{'timestamp': (0,), 'predicted_value': (0,)}]
    else:
        predictions = [{"timestamp": pred.timestamp.isoformat(), "predicted_value": pred.predicted_value} for pred in stored_predictions]
    
    X = pd.DataFrame(historical_data)
    Y = pd.DataFrame(predictions)
    df = pd.merge(X, Y, on="timestamp", how="inner")[-28*24:]
    
    def rmse(y_true, y_pred):
        return np.sqrt(np.mean((y_true - y_pred) ** 2))
    
    rmse_total_elia = 0.0
    rmse_total_pred = 0.0

    if len(df) >= 1:
        rmse_total_elia = rmse(df["total_load"][-24:], df["elia"][-24:])
        rmse_total_pred = rmse(df["total_load"][-24:], df["predicted_value"][-24:])

    elia_errors = (df["total_load"]-df["elia"])
    errors = np.abs(df["total_load"]-df["predicted_value"])
    gain = np.mean(np.abs(elia_errors[-24*7:]) - np.abs(errors[-24*7:]))
    
    limit = 28*24
    return jsonify({
        "historical": historical_data[-limit:], 
        "predictions": predictions[-limit-30:],
        "rmse": {
            "total_load_vs_elia": rmse_total_elia,
            "total_load_vs_predictions": rmse_total_pred
        },
        "gain": gain
    })
    

if __name__ == "__main__":
    app.run(debug=True)
