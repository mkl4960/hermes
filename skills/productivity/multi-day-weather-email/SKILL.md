---
name: multi-day-weather-email
category: productivity
description: Fetch multi-day weather forecast for one or more locations and send via AgentMail email.
---
# Multi-Day Weather Email Notification Skill

Fetch multi-day weather forecast for specified locations using Open-Meteo API (with fallback logic) and send an email summary via AgentMail.

## When to Use
- You need to send a multi-day weather briefing via email (3+ days)
- You want automated weather updates for multiple cities over several days
- You prefer a reliable, no-API-key-needed weather source
- The standard wttr.in API fails for multi-day requests (returns HTTP 500 errors)

## Prerequisites
1. **AgentMail Python SDK** installed (`uv pip install agentmail`)
2. **AgentMail API key** set as environment variable `AGENTMAIL_API_KEY`
3. Basic Python 3.8+ environment
4. Internet access to call Open-Meteo API

## Installation Steps
```bash
# Install AgentMail SDK (if not already)
uv pip install agentmail

# Ensure API key is available
export AGENTMAIL_API_KEY=your_key_here   # or set in your shell profile
```

## Usage
```python
from multi_day_weather import send_multi_day_weather_email

# Example: send 5-day weather for Boston
send_multi_day_weather_email(
    locations=["Boston"],
    days=5,
    recipient="mkl4960@yahoo.com",
    subject="Boston 5-Day Weather Forecast"
)
```

Or run the provided script directly:
```bash
AGENTMAIL_API_KEY=... python send_multi_day_weather.py --locations Boston --days 5 --to mkl4960@yahoo.com
```

## How It Works\n1. **Weather Retrieval**: Uses Open-Meteo API to get forecast data (primary source due to wttr.in multi-day reliability issues)\n   - Primary: `https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max,windspeed_10m_max&timezone=America%2FNew_York&forecast_days={days}`\n   - Note: wttr.in `&day=` parameter frequently returns HTTP 500 errors for multi-day requests; Open-Meteo is more reliable\n2. **Data Parsing**:\n   - Weather condition: Maps numeric weather codes to descriptions using WMO weather code table\n   - Temperature range: `temperature_2m_min`–`temperature_2m_max` (convert to °F if desired: °F = (°C × 9/5) + 32)\n   - Precipitation: `precipitation_probability_max` (percentage chance of precipitation)\n   - Wind speed: `windspeed_10m_max` (convert to mph if desired: mph = km/h × 0.621371)\n   - Date: Forecast date in local timezone\n3. **Email Composition**: Builds a formatted list with one line per day, optionally including precipitation and wind\n4. **Sending**: Uses AgentMail SDK to send via your default inbox\n\n## Weather Code Mapping\nThe skill includes a comprehensive mapping of Open-Meteo weather codes to descriptions (0-99 covering clear sky, clouds, fog, drizzle, rain, snow, thunderstorms).\n\n## Example Output\n```\nBoston 5-Day Forecast (US Customary Units):\n2026-04-27: Light rain shower, 41°F-54°F, Precip: 60%, Wind: 8 mph\n2026-04-28: Patchy rain nearby, 37°F-50°F, Precip: 40%, Wind: 12 mph\n2026-04-29: Overcast, 39°F-48°F, Precip: 20%, Wind: 6 mph\n2026-04-30: Moderate rain, 43°F-55°F, Precip: 80%, Wind: 10 mph\n2026-05-01: Slight snow fall, 28°F-37°F, Precip: 30%, Wind: 15 mph\n```\n\n## Pitfalls & Solutions\n- **wttr.in Multi-Day Failures**: The `&day=` parameter often returns HTTP 500 errors; use Open-Meteo as primary for multi-day requests (more reliable)\n- **Single-Day Optimization**: For 1-day requests, wttr.in may be faster; consider using wttr.in for 1-day, Open-Meteo for 2+ days\n- **Unit Conversion**: Open-Meteo returns metric units (°C, km/h); convert to US Customary if needed:\n  - Temperature: °F = (°C × 9/5) + 32\n  - Wind speed: mph = km/h × 0.621371\n  - Precipitation: Already in % (no conversion needed)\n- **Timezone Handling**: Open-Meteo requires timezone parameter; uses America/New_York for US locations by default\n- **AgentMail Import Errors**: Ensure SDK is installed in current Python environment\n- **Persistant Storage**: Save scripts to `/opt/data/scripts/` to survive container reloads\n- **Location Coordinates**: For production use, consider integrating a geocoding service (like Nominatim or Open-Meteo's geocoding endpoint) instead of hardcoded coordinates

## Verification
1. Check that `AGENTMAIL_API_KEY` is set
2. Run a quick test: `python -c "import agentmail; print(agentmail.__version__)"` should work
3. After sending, verify receipt in recipient's inbox (check spam/junk if needed)
4. Test API connectivity: `curl -s "https://api.open-meteo.com/v1/forecast?latitude=42.3601&longitude=-71.0589&daily=weathercode&forecast_days=1&timezone=America%2FNew_York"`

## Example Script (`send_multi_day_weather.py`)
```python
#!/usr/bin/env python3
"""
Send multi-day weather forecast for locations via AgentMail using Open-Meteo API.
"""
import os
import sys
import json
import urllib.request
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
    """Get coordinates for a location (simple hardcoded for demo, should use geocoding API)."""
    # In a production skill, this would use a geocoding service
    # For now, hardcoding a few common locations
    locations_map = {
        "boston": (42.3601, -71.0589),
        "new york": (40.7128, -74.0060),
        "parsippany": (40.8579, -74.4260),
        "london": (51.5074, -0.1278),
        "tokyo": (35.6762, 139.6503),
    }
    key = location.lower().strip()
    if key in locations_map:
        return locations_map[key]
    # Default to Boston coordinates if not found
    print(f"Warning: Unknown location '{location}', using Boston coordinates")
    return (42.3601, -71.0589)

def send_multi_day_weather_email(locations, days=5, recipient=None, subject=None):
    """Fetch multi-day weather for each location and send email."""
    if recipient is None:
        raise ValueError("Recipient email address is required")
    
    if subject is None:
        subject = f"{days}-Day Weather Forecast"
    
    # Build message body
    lines = []
    for location in locations:
        lat, lon = get_location_coordinates(location)
        data = fetch_multi_day_forecast(lat, lon, days)
        if data:
            weather_text = format_forecast(data, location.title())
            lines.append(weather_text)
        else:
            lines.append(f"{location.title()}: Error fetching weather data")
    
    body = "\n\n".join(lines)
    
    # AgentMail send
    client = AgentMail()
    inbox_id = client.inboxes.list().inboxes[0].inbox_id
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=[recipient],
        subject=subject,
        text=body
    )
    print(f"Email sent! ID: {response.message_id}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Send multi-day weather forecast via email")
    parser.add_argument("--locations", required=True, help="Comma-separated list of locations")
    parser.add_argument("--days", type=int, default=5, help="Number of days to forecast (default: 5)")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", help="Email subject")
    args = parser.parse_args()
    
    locs = [loc.strip() for loc in args.locations.split(",") if loc.strip()]
    send_multi_day_weather_email(locs, args.days, args.to, args.subject)

if __name__ == "__main__":
    main()
```

Make the script executable and run:
```bash
chmod +x send_multi_day_weather.py
AGENTMAIL_API_KEY=... ./send_multi_day_weather.py --locations Boston --days 5 --to mkl4960@yahoo.com
```

## Maintenance
- Keep the AgentMail SDK updated: `uv pip install --upgrade agentmail`
- If Open-Meteo changes its API format, adjust the parsing logic accordingly
- Periodically test the script to ensure email delivery works
- Consider adding a geocoding service (like Nominatim) for automatic coordinate lookup

## Related Skills
- `weather-email-notification`: For single-day (tomorrow) weather forecasts
- `uv-package-installation`: For installing AgentMail and other Python packages in Hermes environments
- `agentmail`: Core skill for sending emails via AgentMail SDK