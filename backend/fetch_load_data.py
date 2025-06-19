import requests
from datetime import datetime, timedelta

BASE_URL = "https://opendata.elia.be/api/records/1.0/search/"

DATASETS = {
    "total_load_historical": "ods001",
    "total_load_realtime": "ods002",
    "system_imbalance_before_220524": "ods047",
    "system_imbalance_after_220524": "ods134",
    "system_imbalance": "ods162"
}

def fetch_data(dataset_id, end_time):
    """
    Fetches the recent data for a given dataset in the past hour.
    """
    start_time = end_time - timedelta(hours=1)

    start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        "dataset": dataset_id,
        "q": f"datetime:[{start_str} TO {end_str}]",
        "rows": 10,
        "sort": "-datetime"
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()
    records = data.get("records", [])
    
    return {record["fields"]["datetime"]: record["fields"] for record in records} if records else {}

def find_common_timestamp(total_load_data, system_imbalance_data):
    """
    Finds the most recent timestamp that is common to both datasets
    and contains the required fields.
    """
    common_timestamps = set(total_load_data.keys()) & set(system_imbalance_data.keys())
    
    for timestamp in sorted(common_timestamps, reverse=True):
        load_entry = total_load_data[timestamp]
        imbalance_entry = system_imbalance_data[timestamp]
        if 'measured' in load_entry:
            load_entry['totalload'] = load_entry['measured']
        
        if all(k in load_entry for k in ['totalload', 'mostrecentforecast']) and 'systemimbalance' in imbalance_entry:
            return timestamp, load_entry, imbalance_entry
    
    return None, None, None

def get_load_data(end_time=datetime.utcnow()+timedelta(hours=1)):
    end_time = end_time.replace(minute=0, second=0)
    if end_time < datetime.today().replace(hour=0, minute=0, second=0):
        total_load_data = fetch_data(DATASETS["total_load_historical"], end_time)
    else:
        total_load_data = fetch_data(DATASETS["total_load_realtime"], end_time)
    if end_time < datetime(2024, 5, 21, 23, 0, 0):
        system_imbalance_data = fetch_data(DATASETS["system_imbalance_before_220524"], end_time)
    elif datetime(2024, 5, 21, 23, 0, 0) <= end_time < datetime.today().replace(hour=0, minute=0, second=0):
        system_imbalance_data = fetch_data(DATASETS["system_imbalance_after_220524"], end_time)
    else:
        system_imbalance_data = fetch_data(DATASETS["system_imbalance"], end_time)

    timestamp, load_entry, imbalance_entry = find_common_timestamp(total_load_data, system_imbalance_data)

    if not total_load_data:
        print("No load data available.")
        return {}
    if not system_imbalance_data:
        print("No system imbalance data available.")
        return {}

    if timestamp and total_load_data and system_imbalance_data:
        return {
            'timestamp': timestamp,
            'total_load': load_entry['totalload'],
            'elia': load_entry['mostrecentforecast'],
            'system_imbalance': imbalance_entry['systemimbalance']
        }
    else:
        print("No common valid data found within the time range.")
        return {}

if __name__ == "__main__":
    for hour in range(15, 24):
        print(get_load_data(datetime(2024, 5, 20, hour)))