#!/usr/bin/env python3
"""
Send 5-day weather forecast for Florham Park, NJ via AgentMail with precipitation and wind in US Customary Units.
"""
import os
import sys
import json
import urllib.request
from agentmail import AgentMail

# Weather code mapping (Open-Meteo)
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

def get_weather_description(code):
    return WEATHER_CODES.get(code, f"Unknown ({code})")

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    if celsius == 'N/A':
        return 'N/A'
    return round((celsius * 9/5) + 32, 1)

def kmh_to_mph(kmh):
    """Convert km/h to mph."""
    if kmh == 'N/A':
        return 'N/A'
    return round(kmh * 0.621371, 1)

def fetch_5day_forecast():
    """Fetch 5-day daily forecast for Florham Park, NJ from Open-Meteo."""
    # Florham Park, NJ coordinates
    latitude = 40.7956
    longitude = -74.4106
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={latitude}&longitude={longitude}"
           f"&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max,windspeed_10m_max"
           f"&timezone=America%2FNew_York&forecast_days=5")
    try:
        with urllib.request.urlopen(url) as resp:
            data = json.load(resp)
        return data
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def format_forecast(data):
    """Format the forecast data into a readable string with US Customary Units."""
    if not data or 'daily' not in data:
        return "No weather data available."
    
    daily = data['daily']
    dates = daily.get('time', [])
    max_temps_c = daily.get('temperature_2m_max', [])
    min_temps_c = daily.get('temperature_2m_min', [])
    weather_codes = daily.get('weathercode', [])
    precip_prob = daily.get('precipitation_probability_max', [])
    wind_speed_kmh = daily.get('windspeed_10m_max', [])
    
    lines = ["Florham Park, NJ 5-Day Forecast (US Customary Units):"]
    for i in range(len(dates)):
        date = dates[i]
        # Convert temperatures to Fahrenheit
        max_temp_f = celsius_to_fahrenheit(max_temps_c[i]) if i < len(max_temps_c) else 'N/A'
        min_temp_f = celsius_to_fahrenheit(min_temps_c[i]) if i < len(min_temps_c) else 'N/A'
        # Convert wind speed to mph
        wind_mph = kmh_to_mph(wind_speed_kmh[i]) if i < len(wind_speed_kmh) else 'N/A'
        
        code = weather_codes[i] if i < len(weather_codes) else None
        description = get_weather_description(code) if code is not None else 'N/A'
        precip = precip_prob[i] if i < len(precip_prob) else 'N/A'
        lines.append(f"{date}: {description}, {min_temp_f}°F-{max_temp_f}°F, Precip: {precip}%, Wind: {wind_mph} mph")
    return "\n".join(lines)

def send_weather_email():
    """Fetch 5-day forecast and send email."""
    data = fetch_5day_forecast()
    if not data:
        body = "Failed to retrieve weather forecast."
    else:
        body = format_forecast(data)
    
    # AgentMail send
    client = AgentMail()
    inbox_id = client.inboxes.list().inboxes[0].inbox_id
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=["mkl4960@yahoo.com"],
        subject="Florham Park, NJ 5-Day Weather Forecast with Precipitation & Wind (US Customary Units)",
        text=body
    )
    print(f"Email sent! ID: {response.message_id}")

if __name__ == "__main__":
    send_weather_email()