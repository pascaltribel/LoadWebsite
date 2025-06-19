from meteostat import Hourly, Stations
from datetime import datetime, timedelta
import pandas as pd
from tqdm.auto import tqdm

def get_belgium_weather(end_time=datetime.utcnow()+timedelta(hours=1)):
    end_time = end_time.replace(minute=0, second=0, microsecond=0)
    start_time = end_time - timedelta(hours=1)

    stations = Stations().region("BE").fetch(10)
    station_ids = stations.index.tolist()

    data = Hourly(station_ids, start_time, end_time).fetch()
    if not data.empty:
        avg_temp = data["temp"].mean()
        avg_precip = data["prcp"].mean() if data["prcp"].mean() >= 0 else 0
        avg_wind = data["wspd"].mean()
        avg_pressure = data["pres"].mean()

        weather_summary = {
            "timestamp": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": avg_temp,
            "precipitation": avg_precip,
            "wind": avg_wind,
            "pressure": avg_pressure,
        }
        return weather_summary

if __name__ == "__main__":
    df = pd.DataFrame(columns=["timestamp", "temperature", "precipitation", "wind", "pressure"])
    start_time = datetime(2015,7,26, hour=0)
    while start_time <= datetime(2025, 3, 25, 0):
        print(start_time)
        df.loc[len(df)] = get_belgium_weather(start_time)
        start_time += timedelta(hours=1)
    df.to_csv("weather.csv")