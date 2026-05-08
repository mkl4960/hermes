---
name: easthanover-weather-email
category: productivity
description: Fetch 5-day weather forecast for East Hanover, NJ and send via AgentMail email.
---
# East Hanover, NJ 5-Day Weather Email Skill

Fetch 5-day weather forecast for East Hanover, NJ using Open-Meteo API and send an email summary via AgentMail.

## When to Use
- You need to send a 5-day weather briefing for East Hanover, NJ via email
- You want automated weather updates for this specific location
- You prefer a reliable, no-API-key-needed weather source (Open-Meteo)

## Prerequisites
1. **AgentMail Python SDK** installed (`uv pip install agentmail`)
2. **AgentMail API key** set as environment variable `AGENTMAIL_API_KEY`
3. Basic Python 3.8+ environment
4. Internet access to call Open-Meteo API and AgentMail API

## Installation Steps
```bash
# Install AgentMail SDK (if not already)
uv pip install agentmail

# Ensure API key is available
export AGENTMAIL_API_KEY=your_key_here   # or set in your shell profile
```

## Usage
```bash
AGENTMAIL_API_KEY=... python /opt/data/scripts/send_easthanover_weather.py
```

Or import and use the function:
```python
from send_easthanover_weather import send_easthanover_weather_email
send_easthanover_weather_email(recipient="mkl4960@gmail.com")
```

## How It Works
1. **Location Geocoding**: Uses coordinates for East Hanover, NJ (40.8200998, -74.3648731)
2. **Weather Retrieval**: Uses Open-Meteo API to get 5-day forecast data
   - API: `https://api.open-meteo.com/v1/forecast?latitude=40.8200998&longitude=-74.3648731&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=America%2FNew_York&forecast_days=5`
3. **Data Parsing**:
   - Weather condition: Maps numeric weather codes to descriptions using WMO weather code table
   - Temperature range: `temperature_2m_min`–`temperature_2m_max` (°C)
4. **Email Composition**: Formats forecast with one line per day (date: condition, min°C-max°C)
5. **Sending**: Uses AgentMail SDK to send via your default inbox

## Weather Code Mapping
The skill includes mapping of Open-Meteo weather codes to descriptions (0-99 covering clear sky, clouds, fog, drizzle, rain, snow, thunderstorms).

## Example Output
```
East Hanover, NJ 5-Day Forecast:
2026-04-26: Dense drizzle, 5.1°C-15.5°C
2026-04-27: Partly cloudy, 4.8°C-18.2°C
2026-04-28: Overcast, 6.1°C-19.3°C
2026-04-29: Overcast, 11.0°C-19.3°C
2026-04-30: Moderate rain showers, 7.9°C-12.0°C
```

## Pitfalls & Solutions
- **AgentMail 403 Forbidden Errors**: If encountering 403 errors when sending, verify:
  1. AgentMail account has email sending permissions enabled
  2. API key has appropriate scopes for sending emails
  3. No sending limits/restrictions on your AgentMail plan
  4. Consider contacting AgentMail support if key should have sending permissions
- **Weather Data Works**: The weather data collection and formatting works correctly even when email sending fails
- **Location Specific**: Script is hardcoded for East Hanover, NJ coordinates
- **Unit Temperature**: Returns temperatures in Celsius (°C)
- **Persistant Storage**: Script saved to `/opt/data/scripts/send_easthanover_weather.py` survives container reloads

## Verification
1. Check that `AGENTMAIL_API_KEY` is set
2. Test AgentMail SDK import: `python -c "import agentmail; print(agentmail.__version__)"`
3. Test weather API connectivity: 
   ```bash
   curl -s "https://api.open-meteo.com/v1/forecast?latitude=40.8200998&longitude=-74.3648731&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=America%2FNew_York&forecast_days=1"
   ```
4. If email sending fails with 403, weather data will still print to console for verification

## Script Location
`/opt/data/scripts/send_easthanover_weather.py`

## Maintenance
- Keep the AgentMail SDK updated: `uv pip install --upgrade agentmail`
- If Open-Meteo changes its API format, adjust the parsing logic accordingly
- Periodically test the script to ensure both weather data collection and email delivery work