---
name: agentmail-persistent-setup
description: Set up AgentMail integrations with persistent storage in Hermes environment
category: email
---
# AgentMail Persistent Setup

Guidelines for setting up AgentMail integrations in the Hermes container environment with persistent storage to ensure scripts, configurations, and cron jobs survive container reloads.

## Trigger Conditions
Use this skill when:
- Setting up automated email sending or monitoring with AgentMail
- Creating scripts that need to persist across container sessions
- You want to ensure AgentMail integrations continue working after container updates

## Environment Overview

### Temporary Storage Issues
- Scripts stored in `/opt/hermes/` are lost on container reload/update
- Cron jobs referencing these paths fail with "file not found" errors
- Environment files and state tracking need special consideration

## Best Practices

### 1. Store AgentMail Scripts Persistently
```bash
# Instead of:
#   /opt/hermes/send_email.py

# Use:
/opt/data/scripts/agentmail/send_email.py

# Ensure directory exists:
mkdir -p /opt/data/scripts/agentmail
```

### 2. Store Configuration and State Persistently
```bash
# Environment files (if not using system env vars)
/opt/data/config/agentmail/.env

# State tracking (e.g., seen message IDs for monitoring)
/opt/data/agentmail/seen_ids.txt

# Ensure directories exist:
mkdir -p /opt/data/config/agentmail
mkdir -p /opt/data/agentmail
```

### 3. Update Cron Jobs to Use Persistent Paths
When creating cron jobs for AgentMail tasks, always reference files in `/opt/data/`:
```bash
# ❌ BROKEN - will fail after container reload:
#   /opt/hermes/.venv/bin/python /opt/hermes/send_weather.py

# ✅ PERSISTENT - will work after container reload:
/opt/hermes/.venv/bin/python /opt/data/scripts/agentmail/send_weather.py
```

### 4. Example: Persistent Weather Email Script
Create `/opt/data/scripts/agentmail/weather_email.py`:
```python
#!/usr/bin/env python3
import os
import json
import urllib.request
from agentmail import AgentMail

def fetch_weather_json(city):
    url = f'https://wttr.in/{city}?format=j1'
    with urllib.request.urlopen(url) as resp:
        return json.load(resp)

def format_hourly(hourly_list):
    lines = []
    for hour in hourly_list:
        time = hour['time']
        if len(time) == 3:
            time = '0' + time
        hh = time[:2]
        mm = time[2:]
        time_str = f"{hh}:{mm}"
        condition = hour['weatherDesc'][0]['value']
        tempf = hour['tempF']
        feelslikef = hour['FeelsLikeF']
        windmph = hour['windspeedMiles']
        winddir = hour['winddir16Point']
        humidity = hour['humidity']
        precipmm = hour['precipMM']
        lines.append(f"{time_str} | {condition:20} | {tempf}°F (feels {feelslikef}°F) | wind {windmph}mph {winddir} | humidity {humidity}% | precip {precipmm}mm")
    return "\n".join(lines)

def main():
    # Fetch weather data
    boston_data = fetch_weather_json('Boston')
    parsippany_data = fetch_weather_json('Parsippany')
    boston_hourly = boston_data['weather'][1]['hourly']
    parsippany_hourly = parsippany_data['weather'][1]['hourly']
    
    boston_section = f"Boston (tomorrow):\n" + format_hourly(boston_hourly)
    parsippany_section = f"Parsippany (tomorrow):\n" + format_hourly(parsippany_hourly)
    
    body = f"""Hi,

Here is the hour-by-hour weather forecast for tomorrow in Fahrenheit:

{boston_section}

{parsippany_section}

Stay dry!
"""

    # Send via AgentMail
    client = AgentMail()
    inbox_id = client.inboxes.list().inboxes[0].inbox_id
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=["mkl4960@yahoo.com"],
        subject="Hour-by-hour Weather Forecast for Tomorrow (°F)",
        text=body
    )
    print(f"Email sent! ID: {response.message_id}")

if __name__ == "__main__":
    main()
```

### 5. Example: Persistent Inbox Monitor Script
Create `/opt/data/scripts/agentmail/monitor_inbox.py`:
```python
#!/usr/bin/env python3
import os
from agentmail import AgentMail

SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'
TARGET_EMAIL = 'laumiex@agentmail.to'
SEARCH_PHRASES = ['URL for', 'CLGNJ English Sunday Worship Service']

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(seen_set):
    with open(SEEN_FILE, 'w') as f:
        for msg_id in sorted(seen_set):
            f.write(msg_id + '\\n')

def main():
    # Load environment variables from .env file
    dotenv_path = '/opt/data/.env'
    if os.path.exists(dotenv_path):
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip().strip('\"').strip(\"'\")
    
    # Get AgentMail API key
    api_key = os.environ.get('AGENTMAIL_API_KEY')
    if not api_key:
        # Silently exit if no API key (appropriate for cron jobs)
        return
    
    seen = load_seen()
    # Initialize client with explicit API key
    client = AgentMail(api_key=api_key)
    
    # Find target inbox
    target_email = TARGET_EMAIL
    inbox_id = None
    for inbox in client.inboxes.list().inboxes:
        if getattr(inbox, 'email', None) == target_email:
            inbox_id = inbox.inbox_id
            break
    if inbox_id is None:
        # Silent failure for cron
        return
    
    # Fetch recent messages
    try:
        messages_resp = client.inboxes.messages.list(inbox_id=inbox_id, limit=50)
        messages = getattr(messages_resp, 'messages', [])
    except Exception:
        # Silent failure for cron
        return
    
    new_matches = []
    for msg in messages:
        msg_id = getattr(msg, 'id', None)
        subject = getattr(msg, 'subject', '') or ''
        if msg_id is None or msg_id in seen:
            continue
        if all(phrase in subject for phrase in SEARCH_PHRASES):
            new_matches.append((msg_id, subject))
    
    if not new_matches:
        # No output for cron
        return
    
    # Update seen set
    for msg in messages:
        msg_id = getattr(msg, 'id', None)
        if msg_id:
            seen.add(msg_id)
    save_seen(seen)
    
    # Print notification(s)
    for msg_id, subject in new_matches:
        print(f"New email matching criteria: {subject}")

if __name__ == '__main__':
    main()
```

## Python Environment and Dependencies

Ensure your AgentMail scripts use a Python interpreter where the `agentmail` package is installed. In the Hermes environment, the recommended approach is to use the Hermes virtual environment located at `/opt/hermes/.venv/`.

#### Using the Hermes Virtual Environment
Set the shebang line to point to the Hermes venv Python:
```python
#!/opt/hermes/.venv/bin/python3
```

#### Installing Dependencies
Use `uv` or `pip` from the Hermes venv to install the AgentMail SDK:
```bash
/opt/hermes/.venv/bin/python -m pip install agentmail
# or using uv (if available in the venv)
uv pip install --python /opt/hermes/.venv/bin/python agentmail
```

#### Alternative: Install in a Persistent Location
If you prefer not to use the Hermes venv, you can create a persistent virtual environment in `/opt/data/`:
```bash
python3 -m venv /opt/data/venv/agentmail
/opt/data/venv/agentmail/bin/pip install agentmail
```

Then update your script's shebang to point to this persistent venv:
```python
#!/opt/data/venv/agentmail/bin/python3
```

Remember to update any cron jobs to reference the correct Python interpreter path.

## Verification
To verify your AgentMail setup is persistent:
1. Create a test script in `/opt/data/scripts/agentmail/test_persistence.py`
2. Set up a cron job to run it
3. Reload/rebuild the container
4. Check if the cron job still runs and the script still exists

## Related Skills
- `hermes-environment/hermes-persistent-storage`: General persistent storage guidelines
- `email/agentmail`: Core AgentMail email sending skill
- `devops/uv-package-installation`: For installing AgentMail SDK persistently

## Quick Reference

| Component | Temporary Location | Persistent Location |
|-----------|-------------------|---------------------|
| Scripts | `/opt/hermes/` | `/opt/data/scripts/agentmail/` |
| Config | `/opt/hermes/` | `/opt/data/config/agentmail/` |
| State | `/opt/hermes/` | `/opt/data/agentmail/` |
| Cron Reference | `/opt/hermes/script.py` | `/opt/data/scripts/agentmail/script.py` |

Remember: Always use `/opt/data/` paths for AgentMail integrations that need to survive container reloads.