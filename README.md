# Total Load Forecasting - Web Visualisation
This module allows the visualisation of our 30-hours step ahead forecaster for the Belgian total electricity load.

## Launching the data server
```bash
cd backend;
./init_db;
python3 app.py;
```

## Launching the php server
```bash
cd frontend;
php -S 127.0.0.1:8000;
```
Then, the web interface can be reached on _127.0.0.1:8000/index.php_.

## Adding points to the database
Currently, the points are extracted from an external `.csv` file (for the simulation part). To simulate the adding of points (by ELIA), do
```bash
cd backend;
python3 simulator.py;
```

The fetch_data files contain the code for fetching data from the portals.
