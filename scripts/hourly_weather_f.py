import os
import json
import urllib.request
import urllib.error
import sys
import time
sys.path.insert(0, '/opt/data/agentmail_packages')
from agentmail import AgentMail

# Weather code to description mapping (WMO codes)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def celsius_to_fahrenheit(c):
    return (c * 9/5) + 32

def kmh_to_mph(kmh):
    return kmh * 0.621371

def fetch_weather_data(latitude, longitude, location_name, retries=3, backoff_factor=1):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relativehumidity_2m,precipitation,weathercode,windspeed_10m,winddirection_10m&timezone=America%2FNew_York'
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url) as resp:
                return json.load(resp)
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))
            else:
                print(f"Failed to fetch weather for {location_name}: {e}", file=sys.stderr)
                return None

def format_hourly(data):
    if not data or 'hourly' not in data:
        return "Weather data unavailable"
    
    hourly = data['hourly']
    times = hourly.get('time', [])
    temps_c = hourly.get('temperature_2m', [])
    humidities = hourly.get('relativehumidity_2m', [])
    precipitations = hourly.get('precipitation', [])
    weathercodes = hourly.get('weathercode', [])
    windspeeds_kmh = hourly.get('windspeed_10m', [])
    winddirections = hourly.get('winddirection_10m', [])
    
    lines = []
    # Only show today's hours (first 24 entries)
    for i in range(min(24, len(times))):
        time_str = times[i][11:16]  # Extract HH:MM from ISO format
        temp_f = celsius_to_fahrenheit(temps_c[i]) if i < len(temps_c) else 0
        humidity = humidities[i] if i < len(humidities) else 0
        precip_mm = precipitations[i] if i < len(precipitations) else 0
        weather_code = weathercodes[i] if i < len(weathercodes) else 0
        condition = WEATHER_CODES.get(weather_code, "Unknown")
        wind_mph = kmh_to_mph(windspeeds_kmh[i]) if i < len(windspeeds_kmh) else 0
        wind_dir = winddirections[i] if i < len(winddirections) else 0
        
        # Convert wind direction degrees to compass point
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(wind_dir / 22.5) % 16
        wind_dir_str = directions[index]
        
        lines.append(f"{time_str} | {condition:20} | {temp_f:3.0f}°F (feels {temp_f:3.0f}°F) | wind {wind_mph:3.0f}mph {wind_dir_str:3} | humidity {humidity:3.0f}% | precip {precip_mm:4.1f}mm")
    
    return "\n".join(lines)

def main():
    # Coordinates for Boston and Parsippany
    locations = [
        {"name": "Boston", "lat": 42.358, "lon": -71.060},
        {"name": "Parsippany", "lat": 40.8579, "lon": -74.426}
    ]
    
    sections = []
    for loc in locations:
        data = fetch_weather_data(loc["lat"], loc["lon"], loc["name"])
        if data:
            section = f"{loc['name']} (today):\n" + format_hourly(data)
            sections.append(section)
        else:
            sections.append(f"{loc['name']} (today): Weather data unavailable")
    
    body = f"""Hi,

Here is the hour-by-hour weather forecast for today in Fahrenheit:

{sections[0]}

{sections[1]}

Stay dry!

"""
    
    client = AgentMail()
    inbox_id = client.inboxes.list().inboxes[0].inbox_id
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=["mkl4960@yahoo.com"],
        subject="Hour-by-hour Weather Forecast for Today (°F)",
        text=body
    )
    print(f"Email sent! ID: {response.message_id}")

if __name__ == "__main__":
    main()