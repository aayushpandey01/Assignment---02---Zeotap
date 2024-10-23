Overview-

This project implements a real-time data processing system to monitor weather conditions and provide summarized insights using rollups and aggregates. The system retrieves weather data from the OpenWeatherMap API for specified cities in India and processes it to generate daily summaries and trigger alerts based on configurable thresholds.

Features-

Fetch real-time weather data from the OpenWeatherMap API at configurable intervals.
Convert temperature values from Kelvin to Celsius.
Calculate daily aggregates: average, maximum, minimum temperature, and dominant weather condition.
Store weather data and daily summaries in an SQLite database.
Trigger alerts if the temperature exceeds a predefined threshold.
Display daily summaries and weather trends using a Flask web interface.

Prerequisites-

Python 3.6+
SQLite
Flask
Requests

Installation-

1. Clone the repository:

   git clone <repository_url>
cd weather-monitoring-system

2. create and activate a virtual environment (optional but recommended):

   python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install required packages:

   pip install -r requirements.txt


Database Setup-

1. Initialize the SQLite database:

   python <script_name>.py
