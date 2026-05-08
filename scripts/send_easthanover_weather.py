#!/usr/bin/env python3
"""
Send 5-day weather forecast for East Hanover, NJ via AgentMail.
"""
import os
import sys
import json
import urllib.request
import subprocess

from agentmail import AgentMail

# Weather code mapping (Open-Meteo)
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

def get_weather_description(code):
    return WEATHER_CODES.get(code, f"Unknown ({code})")

def fetch_multi_day_forecast(latitude, longitude, days, timezone="America/New_York"):
    """Fetch multi-day daily forecast from Open-Meteo."""
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={latitude}&longitude={longitude}"
           f"&daily=weathercode,temperature_2m_max,temperature_2m_min"
           f"&timezone={timezone}&forecast_days={days}")
    try:
        with urllib.request.urlopen(url) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def format_forecast(data, location_name):
    """Format the forecast data into a readable string."""
    if not data or 'daily' not in data:
        return f"{location_name}: No weather data available."
    
    daily = data['daily']
    dates = daily.get('time', [])
    max_temps = daily.get('temperature_2m_max', [])
    min_temps = daily.get('temperature_2m_min', [])
    weather_codes = daily.get('weathercode', [])
    
    lines = [f"{location_name} {len(dates)}-Day Forecast:"]
    for i in range(len(dates)):
        date = dates[i]
        max_temp = max_temps[i] if i < len(max_temps) else 'N/A'
        min_temp = min_temps[i] if i < len(min_temps) else 'N/A'
        code = weather_codes[i] if i < len(weather_codes) else None
        description = get_weather_description(code) if code is not None else 'N/A'
        lines.append(f"{date}: {description}, {min_temp}°C-{max_temp}°C")
    return "\n".join(lines)

def get_location_coordinates(location):
    """Get coordinates for a location using the maps skill."""
    # Use the maps script to search for the location
    maps_script = "/opt/data/skills/productivity/maps/scripts/maps_client.py"
    cmd = [
        sys.executable,
        maps_script,
        "search",
        location
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"Warning: Maps script failed for '{location}': {result.stderr}")
            # Fallback to a known location (Boston) as before
            return (42.3601, -71.0589)
        # Parse the JSON output from maps script
        data = json.loads(result.stdout.strip())
        # The maps script output has a 'results' key
        if data.get("results"):
            first = data["results"][0]
            lat = float(first["lat"])
            lon = float(first["lon"])
            return lat, lon
        else:
            print(f"Warning: No results found for '{location}' using maps script")
            # Fallback to Boston
            return (42.3601, -71.0589)
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse maps script output as JSON: {e}")
        print(f"Output was: {result.stdout[:200]}")
        # Fallback to Boston
        return (42.3601, -71.0589)
    except Exception as e:
        print(f"Warning: Error geocoding '{location}': {e}")
        # Fallback to Boston
        return (42.3601, -71.0589)

def send_weather_email(location, days=5, recipient=None, subject=None):
    """Fetch multi-day weather for location and send email."""
    if recipient is None:
        raise ValueError("Recipient email address is required")
    
    if subject is None:
        subject = f"{days}-Day Weather Forecast for {location}"
    
    # Get coordinates
    lat, lon = get_location_coordinates(location)
    print(f"Coordinates for {location}: lat={lat}, lon={lon}")
    # Fetch weather data
    data = fetch_multi_day_forecast(lat, lon, days)
    if not data:
        print(f"Error: Could not fetch weather data for {location}")
        return False
    
    # Format forecast
    body = format_forecast(data, location)
    print(f"Forecast body:\n{body}")
    
    # Send via AgentMail
    try:
        # Get API key from environment
        api_key = os.environ.get('AGENTMAIL_API_KEY')
        if not api_key:
            print("Error: AGENTMAIL_API_KEY not set")
            return False
        # Mask the API key for printing (show first 10 and last 4 characters)
        masked_key = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 14 else "***"
        print(f"Using API key: {masked_key}")
        client = AgentMail(api_key=api_key)
        # Use the known inbox ID for the AgentMail email laumiex@agentmail.to
        inbox_id = 'laumiex@agentmail.to'
        response = client.inboxes.messages.send(
            inbox_id=inbox_id,
            to=[recipient],
            subject=subject,
            text=body
        )
        print(f"Email sent! ID: {response.message_id}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    location = "East Hanover, NJ"
    days = 5
    recipient = "mkl4960@gmail.com"
    success = send_weather_email(location, days, recipient)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()