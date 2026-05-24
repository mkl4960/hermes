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

## Core Components

### 1. Weather Data Fetching
Retrieving weather forecasts from APIs and web services.

### 2. Email Composition and Sending
Formatting weather data into readable emails and sending via AgentMail.

### 3. Persistent Storage Setup
Storing weather email scripts and configurations persistently to survive container reloads.

### 4. Scheduling and Automation
Configuring cron jobs or other scheduling mechanisms for regular weather emails.

### 5. Customization and Formatting
Tailoring weather email appearance, units, and included information.

## Quick Reference

| Component | Purpose | Key Files/Directories |
|-----------|---------|----------------------|
| **Data Fetching** | Get weather forecasts | wttr.in API, OpenWeatherMap, etc. |
| **Email Sending** | Send weather alerts | AgentMail integration |
| **Persistence** | Survive container reloads | `/opt/data/scripts/weather/`, `/opt/data/config/weather/` |
| **Scheduling** | Regular automated delivery | Cron jobs referencing `/opt/data/` paths |
| **Customization** | Tailor content and format | Script modifications, templates |

## Environment Setup

Before using any weather email functionality, ensure:
1. AgentMail Python SDK is installed and configured
2. Persistent storage directories exist for scripts and config
3. Weather API access is configured (if needed)
4. Cron jobs reference persistent paths

## Common Patterns

### Basic Weather Email Structure
```python
#!/opt/hermes/.venv/bin/python3
import os
import json
import urllib.request
from agentmail import AgentMail

def fetch_weather_data(location):
    # Fetch weather data from your preferred source
    url = f'https://wttr.in/{location}?format=j1'
    with urllib.request.urlopen(url) as resp:
        return json.load(resp)

def format_weather_email(weather_data):
    # Format weather data into email body
    # Customize this function for your preferred format
    pass

def main():
    # Load environment and send email
    client = AgentMail()
    # ... email sending logic
    pass

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