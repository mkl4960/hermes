---
name: weather-email-notification
category: productivity
description: Fetch tomorrow's weather forecast for one or more locations and send via AgentMail email.
---
# Weather Email Notification Skill

Fetch tomorrow's weather forecast for specified locations using wttr.in and send an email summary via AgentMail.

## When to Use
- You need to send a daily weather briefing via email
- You want automated weather updates for multiple cities
- You prefer a lightweight, no-API-key-needed weather source (wttr.in)

## Prerequisites
1. **AgentMail Python SDK** installed (`uv pip install agentmail`)
2. **AgentMail API key** set as environment variable `AGENTMAIL_API_KEY`
3. Basic Python 3.8+ environment

## Installation Steps
```bash
# Install AgentMail SDK (if not already)
uv pip install agentmail

# Ensure API key is available
export AGENTMAIL_API_KEY=your_key_here   # or set in your shell profile
```

## Usage
```python
from weather_email import send_weather_email

# Example: send weather for Boston and Parsippany
send_weather_email(
    locations=["Boston", "Parsippany"],
    recipient="mkl4960@yahoo.com",
    subject="Tomorrow's Weather Forecast"
)
```

Or run the provided script directly:
```bash
AGENTMAIL_API_KEY=... python send_weather_email.py --locations Boston,Parsippany --to mkl4960@yahoo.com
```

## How It Works
1. **Weather Retrieval**: Uses `wttr.in/{city}?format=j1` to get JSON forecast data.
2. **Tomorrow's Forecast**: Extracts `weather[1]` (today = index 0, tomorrow = index 1).
3. **Data Parsing**:
   - Condition: weather description at noon (`hourly` where `time == "1200"`, else first hour).
   - Temperature range: `mintempC`–`maxtempC`.
   - Wind speed: `windspeedKmph` at noon (or first hour).
   - Humidity: `humidity` at noon (or first hour).
4. **Email Composition**: Builds a plain‑text bullet list.
5. **Sending**: Uses AgentMail SDK to send via your default inbox.

## Example Output
```
Boston tomorrow: Light rain shower, 5-12°C, wind 6km/h, humidity 96%
Parsippany tomorrow: Patchy rain nearby, 3-10°C, wind 15km/h, humidity 45%
```

## Pitfalls & Solutions
- **500 Error from wttr.in with `&day=1`**: The `day` parameter sometimes fails; use the JSON endpoint and index into the `weather` array instead.
- **Missing Noon Data**: If the `hourly` array lacks an entry for `"1200"`, fall back to the first hour's data.
- **AgentMail Import Errors**: Ensure the SDK is installed in the current Python environment (use `uv pip install agentmail` or activate the venv).
- **Permission Denied on .venv**: When using a Hermes-managed venv, run scripts with the venv's Python directly (`/opt/hermes/.venv/bin/python script.py`) rather than `uv run` which may trigger rebuilds.

## Verification
1. Check that `AGENTMAIL_API_KEY` is set.
2. Run a quick test: `python -c "import agentmail; print(agentmail.__version__)"` should show `0.4.15` or later.
3. After sending, verify receipt in the recipient's inbox (check spam/junk if needed).

## Example Script (`send_weather_email.py`)
```python
#!/usr/bin/env python3
"""
Send tomorrow's weather for multiple locations via AgentMail.
"""
import os
import sys
import json
import urllib.request
from agentmail import AgentMail

def get_tomorrow_weather(city: str) -> str:
    """Fetch and format tomorrow's weather for a city."""
    url = f"https://wttr.in/{city}?format=j1"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    tomorrow = data["weather"][1]  # index 0 = today, 1 = tomorrow
    hourly = tomorrow["hourly"]

    # Find noon (12:00) entry; else use first hour
    noon = next((h for h in hourly if h["time"] == "1200"), hourly[0])

    condition = noon["weatherDesc"][0]["value"]
    mintemp = tomorrow["mintempC"]
    maxtemp = tomorrow["maxtempC"]
    wind = noon["windspeedKmph"]
    humidity = noon["humidity"]
    return f"{condition}, {mintemp}-{maxtemp}°C, wind {wind}km/h, humidity {humidity}%"

def send_weather_email(locations, recipient, subject="Weather Forecast"):
    """Fetch weather for each location and send email."""
    # Build message body
    lines = []
    for loc in locations:
        try:
            weather = get_tomorrow_weather(loc)
            lines.append(f"{loc}: {weather}")
        except Exception as e:
            lines.append(f"{loc}: Error fetching weather ({e})")
    body = "\n".join(lines)

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
    parser = argparse.ArgumentParser(description="Send tomorrow's weather via email")
    parser.add_argument("--locations", required=True, help="Comma-separated list of locations")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--subject", default="Tomorrow's Weather Forecast", help="Email subject")
    args = parser.parse_args()
    locs = [loc.strip() for loc in args.locations.split(",") if loc.strip()]
    send_weather_email(locs, args.to, args.subject)

if __name__ == "__main__":
    main()
```

Make the script executable and run:
```bash
chmod +x send_weather_email.py
AGENTMAIL_API_KEY=... ./send_weather_email.py --locations Boston,Parsippany --to mkl4960@yahoo.com
```

## Maintenance
- Keep the AgentMail SDK updated: `uv pip install --upgrade agentmail`
- If wttr.in changes its JSON format, adjust the parsing logic accordingly.
- Periodically test the script to ensure email delivery works.

---