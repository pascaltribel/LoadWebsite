from database_engine import SessionLocal
from models import Data
from datetime import datetime
import pandas as pd
from tqdm.auto import tqdm


def insert_entry(db = SessionLocal(), 
                 timestamp=datetime.now(), 
                 total_load = 0.0,
                 total_load_1_year_before = 0.0,
                 system_imbalance = 0.0,
                 temperature = 0.0,
                 precipitation = 0.0,
                 wind = 0.0,
                 pressure = 0.0,
                 elia=0.0):
    new_entry = Data(timestamp=timestamp, 
                     total_load = total_load,
                     total_load_1_year_before = total_load_1_year_before,
                     system_imbalance = system_imbalance,
                     temperature = temperature,
                     precipitation = precipitation,
                     wind = wind,
                     pressure = pressure,
                     elia=elia)
    db.add(new_entry)
    db.commit()
    db.close()
data = pd.read_csv("../data/final_data.csv", index_col=0)
correspondances = {'Datetime': 'timestamp', 
                   'Total Load': 'total_load', 
                   'Total Load 1 Year Before, to the FH': 'total_load_1_year_before',
                   'System imbalance': 'system_imbalance', 
                   'Temperature': 'temperature', 
                   'Precipitation': 'precipitation', 
                   'Wind': 'wind', 
                   'Pressure': 'pressure',
                   'Most recent forecast': 'elia'}

if __name__ == "__main__":
    for index, row in tqdm(data.iterrows()):
        # Map the row values to the corresponding columns in the Data model
        entry_data = {correspondances[key]: row[key] for key in correspondances}
        
        # Insert the entry into the database
        insert_entry(
            db=SessionLocal(),
            timestamp=datetime.strptime(entry_data['timestamp'], "%Y-%m-%d %H:%M:%S+00:00"),  # Convert timestamp to datetime
            total_load=entry_data['total_load'],
            total_load_1_year_before=entry_data['total_load_1_year_before'],
            system_imbalance=entry_data['system_imbalance'],
            temperature=entry_data['temperature'],
            precipitation=entry_data['precipitation'],
            wind=entry_data['wind'],
            pressure=entry_data['pressure'],
            elia=entry_data['elia']
        )
        if index == 30000:
            break