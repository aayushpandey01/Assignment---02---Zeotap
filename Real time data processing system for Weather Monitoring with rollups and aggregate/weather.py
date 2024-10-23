import requests
import time
import sqlite3
from collections import defaultdict
from datetime import datetime
from flask import Flask, render_template, jsonify

API_KEY = 'your_api_key_here'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
INTERVAL = 300  
DB_PATH = 'weather.db'
THRESHOLD = 35


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                temp REAL NOT NULL,
                feels_like REAL NOT NULL,
                dt INTEGER NOT NULL,
                condition TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                date TEXT NOT NULL,
                avg_temp REAL,
                max_temp REAL,
                min_temp REAL,
                dominant_condition TEXT
            )
        """)
    return conn


def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    response = requests.get(url)
    return response.json()


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15


def process_weather_data(conn, city, weather_data):
    temp_celsius = kelvin_to_celsius(weather_data['main']['temp'])
    feels_like_celsius = kelvin_to_celsius(weather_data['main']['feels_like'])
    dt = weather_data['dt']
    condition = weather_data['weather'][0]['main']
    
    with conn:
        conn.execute("""
            INSERT INTO weather (city, temp, feels_like, dt, condition)
            VALUES (?, ?, ?, ?, ?)
        """, (city, temp_celsius, feels_like_celsius, dt, condition))
        
    daily_data[city].append(temp_celsius)


def calculate_daily_summary(conn, city):
    temps = daily_data[city]
    if temps:
        avg_temp = sum(temps) / len(temps)
        max_temp = max(temps)
        min_temp = min(temps)
        dominant_condition = max(set(temps), key=temps.count)
        date = datetime.now().strftime('%Y-%m-%d')
        
        with conn:
            conn.execute("""
                INSERT INTO daily_summary (city, date, avg_temp, max_temp, min_temp, dominant_condition)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (city, date, avg_temp, max_temp, min_temp, dominant_condition))


def check_alerts(city, temp):
    if temp > THRESHOLD:
        print(f'Alert! {city} temperature exceeded {THRESHOLD}°C')


app = Flask(__name__)
conn = init_db()
daily_data = defaultdict(list)


def fetch_weather_data():
    while True:
        for city in CITIES:
            weather_data = get_weather(city)
            process_weather_data(conn, city, weather_data)
            temp_celsius = kelvin_to_celsius(weather_data['main']['temp'])
            check_alerts(city, temp_celsius)
        time.sleep(INTERVAL)


import threading
thread = threading.Thread(target=fetch_weather_data)
thread.daemon = True
thread.start()


@app.route('/')
def index():
    summaries = {}
    for city in CITIES:
        date = datetime.now().strftime('%Y-%m-%d')
        cur = conn.execute("""
            SELECT * FROM daily_summary WHERE city = ? AND date = ?
        """, (city, date))
        summaries[city] = cur.fetchone()
    return render_template('index.html', summaries=summaries)

@app.route('/api/weather')
def api_weather():
    data = {}
    for city in CITIES:
        cur = conn.execute("""
            SELECT * FROM weather WHERE city = ? ORDER BY dt DESC LIMIT 1
        """, (city,))
        data[city] = cur.fetchone()
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
