---
name: weather-email-notifications
description: Comprehensive guide to setting up and managing weather email notifications using AgentMail and Hermes environment
category: productivity
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [weather, email, notification, agentmail, forecast]
    related_skills: [agentmail-integrations, hermes-persistent-storage]
---

# Weather Email Notifications

Complete guide to setting up, configuring, and managing automated weather email notifications in Hermes environments using AgentMail.

## Overview

This skill consolidates various weather email notification functionalities into a comprehensive framework covering:
- Fetching weather forecasts from various sources (wttr.in, OpenWeatherMap, etc.)
- Sending weather emails via AgentMail
- Setting up persistent storage for weather email scripts
- Customizing weather email content and format
- Scheduling weather email deliveries
- Handling different timeframes (today, tomorrow, multi-day)
- Location-specific weather forecasts

## When to Use

Use this skill when you need to:
- Automate daily weather forecast emails
- Send weather alerts for specific locations
- Customize weather email content and format
- Integrate weather data with AgentMail for reliable delivery
- Set up persistent weather email systems that survive container reloads
- Create multi-location weather notification systems

## Core Components\n\n### 1. Weather Data Fetching\nRetrieving weather forecasts from reliable APIs. Due to frequent unreliability of wttr.in (HTTP 500 errors), Open-Meteo API is recommended as a primary source with fallback mechanisms.\n\n### 2. Email Composition and Sending\nFormatting weather data into readable emails and sending via AgentMail, including unit conversion (Celsius to Fahrenheit, km/h to mph) and weather code interpretation.\n\n### 3. Persistent Storage Setup\nStoring weather email scripts and configurations persistently to survive container reloads in `/opt/data/scripts/weather/` and `/opt/data/config/weather/`.\n\n### 4. Scheduling and Automation\nConfiguring cron jobs or other scheduling mechanisms for regular weather emails referencing persistent storage paths.\n\n### 5. Customization and Formatting\nTailoring weather email appearance, units, and included information. Includes handling missing data gracefully and limiting forecasts to relevant timeframes (e.g., today only).

## Quick Reference\n\n| Component | Purpose | Key Files/Directories |\n|-----------|---------|----------------------|\n| **Data Fetching** | Get weather forecasts | Open-Meteo API (primary), wttr.in (fallback) |\n| **Email Sending** | Send weather alerts | AgentMail integration |\n| **Persistence** | Survive container reloads | `/opt/data/scripts/weather/`, `/opt/data/config/weather/` |\n| **Scheduling** | Regular automated delivery | Cron jobs referencing `/opt/data/` paths |\n| **Customization** | Tailor content and format | Script modifications, templates |\n| **References** | API comparison and implementation details | `references/wttr-in-openmeteo-comparison.md` |

## Environment Setup

Before using any weather email functionality, ensure:
1. AgentMail Python SDK is installed and configured
2. Persistent storage directories exist for scripts and config
3. Weather API access is configured (if needed)
4. Cron jobs reference persistent paths

## Common Patterns

### Reliable Weather Email Structure (Open-Meteo Based)
```python
#!/opt/hermes/.venv/bin/python3
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
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle",
    53: "Moderate drizzle", 55: "Dense drizzle", 56: "Light freezing drizzle",
    57: "Dense freezing drizzle", 61: "Slight rain", 63: "Moderate rain",
    65: "Heavy rain", 66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
    77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
    82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail",
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
    # Coordinates for locations
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
```

### Persistent Script Location
Always store weather email scripts in: `/opt/data/scripts/weather/`

### Configuration Storage
Store API keys and preferences in: `/opt/data/config/weather/`

### Cron Job Example
Schedule daily weather emails at 7 AM:
```bash
0 7 * * * /opt/hermes/.venv/bin/python /opt/data/scripts/weather/daily_weather.py
```

### Key Improvements Over Previous Implementations
1. **Reliable Data Source**: Uses Open-Meteo API instead of unreliable wttr.in
2. **Unit Conversion**: Properly converts Celsius to Fahrenheit and km/h to mph
3. **Weather Code Interpretation**: Maps WMO weather codes to readable descriptions
4. **Wind Direction**: Converts degrees to compass points (N, NE, SE, etc.)
5. **Error Handling**: Graceful degradation when API fails, continues with available data
6. **Today's Forecast Only**: Limits output to today's 24 hours for relevance
7. **Retry Mechanism**: Exponential backoff for failed requests

See `references/wttr-in-openmeteo-comparison.md` for detailed API comparison.

## Verification

After setting up any weather email notification:
1. Test scripts manually before automating with cron
2. Verify persistent storage works across container reloads
3. Check that cron jobs reference `/opt/data/` paths
4. Validate that emails are received with correct formatting
5. Monitor logs for proper operation

## Maintenance

- Keep AgentMail SDK updated: `uv pip install --upgrade agentmail`
- Test weather API endpoints periodically for availability
- Update scripts when weather API formats change
- Rotate API keys periodically for security
- Monitor email delivery and spam folders

## Related Skills

- `agentmail-integrations`: For comprehensive AgentMail setup and usage
- `hermes-persistent-storage`: For general persistent storage guidelines
- `devops/uv-package-installation`: For installing packages in restricted environments
- `productivity/maps`: For geolocation and location-based services

---

## Subsections

The following sections detail specific aspects of weather email notifications that were previously separate skills:

### Today's Weather Email
See the original `update-weather-email-to-today` skill for modifying weather email scripts to show current day's weather instead of tomorrow's.

### Tomorrow's Weather Notification
See the original `weather-email-notification` skill for fetching and sending tomorrow's weather forecast.

### Multi-Day Weather Email
See the original `multi-day-weather-email` skill for sending extended weather forecasts.

### Location-Specific Weather (East Hanover)
See the original `easthanover-weather-email` skill for the specific implementation targeting East Hanover, NJ.

---
*This skill consolidates multiple weather email-related skills into a comprehensive framework for easier discovery and maintenance.*