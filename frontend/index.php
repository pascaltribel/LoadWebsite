<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Electricity Prediction</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Total Load Forecasting: 30-hours ahead</h1>

    <div id="stats">
        <h2>System Statistics</h2>
        <div class="stat-item">Current Time: <span id="currentTime"></span></div>
        <div class="stat-item">Last Update: <span id="lastTimestamp"></span></div>
        <div class="stat-item">Average Load (4 weeks): <span id="meanLoad"></span></div>
    </div>
    <div id="stats">
        <h2>Benchmark and Forecasts</h2>
        <div class="stat-item">Forecasted Load (30h): <span id="latestForecast"></span></div>
        <div class="stat-item">RMSE ELIA (last day): <span id="rmseELIA"></span></div>
        <div class="stat-item">RMSE (last day): <span id="rmse"></span></div>
        <div class="stat-item">Estimated gain (RMSE - last day): <span id="gain"></span></div>
    </div>

    <label for="daysSelect">Historical duration display: </label>
    <select id="daysSelect" onchange="fetchData()">
        <option value="1">1 day</option>
        <option value="2">2 days</option>
        <option value="3">3 days</option>
        <option value="7" selected>1 week</option>
        <option value="14">2 weeks</option>
        <option value="21">3 weeks</option>
        <option value="28">4 weeks</option>
    </select>

    <canvas id="loadChart"></canvas>

    <div class="frame">
        <div class="tabs">
            <button class="tab-button active" onclick="showTab('temperatureTab')">Temperature</button>
            <button class="tab-button" onclick="showTab('windTab')">Wind Speed</button>
            <button class="tab-button" onclick="showTab('pressureTab')">Pressure</button>
            <button class="tab-button" onclick="showTab('precipitationsTab')">Precipitations</button>
        </div>
        <div id="temperatureTab" class="tab-content active">
            <canvas id="temperatureChart"></canvas>
        </div>
        <div id="windTab" class="tab-content">
            <canvas id="windChart"></canvas>
        </div>
        <div id="pressureTab" class="tab-content">
            <canvas id="pressureChart"></canvas>
        </div>
        <div id="precipitationsTab" class="tab-content">
            <canvas id="precipitationsChart"></canvas>
        </div>
    </div>


    <script>
        let charts = {};

        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));

            document.getElementById(tabId).style.display = 'block';
            document.querySelector(`[onclick="showTab('${tabId}')"]`).classList.add('active');
        }

        document.addEventListener("DOMContentLoaded", function () {
            document.querySelector('.tab-content.active').style.display = 'block';
        });



        function calculateMean(values) {
            const sum = values.reduce((a, b) => a + b, 0);
            return sum / values.length;
        }

        function convertTemp(value) {
            return useFahrenheit ? (value * 9/5) + 32 : value;
        }

        async function fetchData() {
            try {
                const response = await fetch("http://127.0.0.1:5000/data");
                const data = await response.json();
                
                const daysSelected = parseInt(document.getElementById("daysSelect").value, 10);
                const numEntries = daysSelected * 24;  

                const filteredHistorical = data.historical.slice(-numEntries);
                const filteredPredictions = data.predictions.slice(-numEntries-30);
                
                updateCharts(filteredPredictions, filteredHistorical);
                updateStats(data);
            } catch (error) {
                console.error(error);
            }
        }

        function extendWithMissingPoints(data, lastTimestamp) {
            let extendedData = [...data];
            let numericLastTimestamp = new Date(lastTimestamp).getTime();

            for (let i = 1; i < 30; i++) {
                extendedData.push({ x: new Date(numericLastTimestamp + i * 3600000).toISOString(), y: null });
            }
            return extendedData;
        };
        function updateCharts(filteredPredictions, filteredHistorical) {
            const historicalLoad = filteredHistorical.map(entry => ({ x: entry.timestamp, y: entry.total_load }));
            const historicalElia = filteredHistorical.map(entry => ({ x: entry.timestamp, y: entry.elia }));
            const historicalTemp = extendWithMissingPoints(
                filteredHistorical.map(entry => ({ x: entry.timestamp, y: entry.temperature })), 
                historicalLoad[historicalLoad.length - 1].x
            );
            const historicalWind = extendWithMissingPoints(
                filteredHistorical.map(entry => ({ x: entry.timestamp, y: entry.wind })), 
                historicalLoad[historicalLoad.length - 1].x
            );
            const historicalPressure = extendWithMissingPoints(
                filteredHistorical.map(entry => ({ x: entry.timestamp, y: entry.pressure })), 
                historicalLoad[historicalLoad.length - 1].x
            );
            const historicalPrecipitations = extendWithMissingPoints(
                filteredHistorical.map(entry => ({ x: entry.timestamp, y: entry.precipitation })), 
                historicalLoad[historicalLoad.length - 1].x
            );
            const predictionsLoad = filteredPredictions.map(entry => ({ x: entry.timestamp, y: entry.predicted_value }));


            
            if (!charts.load) {
                const ctx = document.getElementById("loadChart")?.getContext('2d');
                if (ctx) {
                    charts.load = new Chart(ctx, {
                        type: 'line',
                        data: { datasets: [
                            { label: "Total Load", data: historicalLoad, borderColor: "rgb(255, 0, 0)", fill: false },
                            { label: "Forecast", data: predictionsLoad, borderColor: "rgb(0, 135, 32)", borderDash: [5, 5], fill: false },
                            { label: "Elia", data: historicalElia, borderColor: "rgb(255, 242, 0)", fill: false },
                        ] },
                        options: { animation: true, responsive: false, scales: { x: { type: 'time' } } }
                    });
                }
            } else {
                charts.load.data.datasets[0].data = historicalLoad;
                charts.load.data.datasets[1].data = predictionsLoad;
                charts.load.data.datasets[2].data = historicalElia;
                charts.load.update();
            }
            if (!charts.temp) {
                const ctx = document.getElementById("temperatureChart")?.getContext('2d');
                if (ctx) {
                    charts.temp = new Chart(ctx, {
                        type: 'line',
                        data: { datasets: [
                            { label: "Temperature", data: historicalTemp, borderColor: "rgb(33, 211, 2)", fill: false }
                        ] },
                        options: { animation: true, responsive: false, scales: { x: { type: 'time' } } }
                    });
                }
            } else {
                charts.temp.data.datasets[0].data = historicalTemp;
                charts.temp.update();
            }
            if (!charts.wind) {
                const ctx = document.getElementById("windChart")?.getContext('2d');
                if (ctx) {
                    charts.wind = new Chart(ctx, {
                        type: 'line',
                        data: { datasets: [
                            { label: "Wind", data: historicalWind, borderColor: "rgb(211, 2, 162)", fill: false }
                        ] },
                        options: { animation: true, responsive: false, scales: { x: { type: 'time' } } }
                    });
                }
            } else {
                charts.wind.data.datasets[0].data = historicalWind;
                charts.wind.update();
            }
            if (!charts.pressure) {
                const ctx = document.getElementById("pressureChart")?.getContext('2d');
                if (ctx) {
                    charts.pressure = new Chart(ctx, {
                        type: 'line',
                        data: { datasets: [
                            { label: "Pressure", data: historicalPressure, borderColor: "rgb(33, 2, 211)", fill: false }
                        ] },
                        options: { animation: true, responsive: false, scales: { x: { type: 'time' } } }
                    });
                }
            } else {
                charts.pressure.data.datasets[0].data = historicalPressure;
                charts.pressure.update();
            }
            if (!charts.precipitations) {
                const ctx = document.getElementById("precipitationsChart")?.getContext('2d');
                if (ctx) {
                    charts.precipitations = new Chart(ctx, {
                        type: 'line',
                        data: { datasets: [
                            { label: "Precipitations", data: historicalPrecipitations, borderColor: "rgb(0, 200, 255)", fill: false }
                        ] },
                        options: { animation: true, responsive: false, scales: { x: { type: 'time' } } }
                    });
                }
            } else {
                charts.precipitations.data.datasets[0].data = historicalPrecipitations;
                charts.precipitations.update();
            }
        }


        function updateStats(data) {
            const timestamps = data.historical.map(entry => entry.timestamp);
            const values = data.historical.map(entry => entry.total_load);
            const meanLoad = calculateMean(values);
            const lastTimestamp = new Date(timestamps[timestamps.length - 1]).toLocaleString();
            const latestForecast = data.predictions.length ? data.predictions[data.predictions.length - 1].predicted_value : 'N/A';
            const eliaRMSE = data.rmse.total_load_vs_elia;
            const rmse = data.rmse.total_load_vs_predictions;
            const gain = data.gain;

            document.getElementById('lastTimestamp').textContent = lastTimestamp;
            document.getElementById('meanLoad').textContent = meanLoad.toFixed(2);
            document.getElementById('latestForecast').textContent = latestForecast.toFixed(2);
            document.getElementById('currentTime').textContent = new Date().toLocaleTimeString();
            document.getElementById('rmseELIA').textContent = eliaRMSE.toFixed(2);
            document.getElementById('rmse').textContent = rmse.toFixed(2);
            document.getElementById('gain').textContent = (gain).toFixed(2);
        }

        fetchData();
        setInterval(fetchData, 200);
    </script>
</body>
</html>