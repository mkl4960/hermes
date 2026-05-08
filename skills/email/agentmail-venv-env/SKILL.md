---
name: agentmail-venv-env
category: email
description: Reusable approach for sending emails via AgentMail SDK that guarantees use of the Hermes virtual environment and loading API keys from .env file.
---
# AgentMail with Virtualenv and .env

Reusable approach for sending emails via AgentMail SDK that guarantees:
- Use of the Hermes virtual environment (`/opt/hermes/.venv/bin/python`)
- Loading of API keys from `/opt/data/.env` (or any .env file)
- No hard‑coded secrets, no reliance on the default system Python

## When to Use
- You need to send email via AgentMail in any Hermes session or cron job.
- You want a repeatable, zero‑setup command that works regardless of the current shell's PATH or environment variables.

## Prerequisites
1. The Hermes virtual environment exists at `/opt/hermes/.venv` (standard in Hermes).
2. A `.env` file containing `AGENTMAIL_API_KEY=your_key_here` (default location `/opt/data/.env`).
3. The AgentMail Python SDK installed in the venv (already present; otherwise run `/opt/hermes/.venv/bin/uv pip install agentmail`).

## Steps

### 1. Prepare a Python script (or use the provided template)
Create a script that:
- Imports `os`, `json`, `urllib.request` (or any other libs you need).
- Loads the `.env` file (optional: use `python-dotenv` or manual parsing).
- Initializes the AgentMail client (`from agentmail import AgentMail` or `from agentmail.client import AgentMail`).
- Sends the email.

**Example script** (`send_email.py`):
```python
#!/opt/hermes/.venv/bin/python3
import os
import json
import urllib.request
from agentmail import AgentMail

# ---- Load .env (simple parser) ----
def load_dotenv(path='/opt/data/.env'):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

load_dotenv()  # populates AGENTMAIL_API_KEY

# ---- Your email logic here ----
def get_tomorrow_weather(city):
    url = f"https://wttr.in/{city}?format=j1"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    tomorrow = data["weather"][1]
    hourly = tomorrow["hourly"]
    noon = next((h for h in hourly if h["time"] == "1200"), hourly[0])
    condition = noon["weatherDesc"][0]["value"]
    mintemp = tomorrow["mintempC"]
    maxtemp = tomorrow["maxtempC"]
    wind = noon["windspeedKmph"]
    humidity = noon["humidity"]
    return f"{condition}, {mintemp}-{maxtemp}°C, wind {wind}km/h, humidity {humidity}%"

weather = get_tomorrow_weather("Boston")
body = f"Boston tomorrow: {weather}\n\nDryer troubleshooting steps..."  # fill as needed

client = AgentMail()
inbox_id = client.inboxes.list().inboxes[0].inbox_id
resp = client.inboxes.messages.send(
    inbox_id=inbox_id,
    to=["mkl4960@yahoo.com"],
    subject="Boston Weather Tomorrow & Dryer Troubleshooting Guide",
    text=body
)
print(f"Sent: {resp.message_id}")
```

Make it executable: `chmod +x send_email.py`.

### 2. Execute using the venv Python
From any shell (including cron), run:
```bash
source /opt/data/.env && /opt/hermes/.venv/bin/python /path/to/send_email.py
```
*The `source /opt/data/.env` line ensures the API key is in the environment for the subprocess; the script also reloads the .env for safety.*

### 3. For cron jobs
When creating a cron job via the `cronjob` tool, set:
- `script`: optional wrapper that sources .env then calls the venv python (or rely on the script’s internal .env load).
- Or embed the `source` command directly in the cron `prompt`.

**Example cron create**:
```json
{
  "action": "create",
  "name": "daily-weather-email",
  "prompt": "source /opt/data/.env && /opt/hermes/.venv/bin/python /opt/data/send_weather_dryer.py",
  "schedule": "0 7 * * *",
  "deliver": "origin"
}
```

## Why This Works
- The virtual environment’s Python guarantees the correct `agentmail` module version.
- Loading the `.env` file (either via `source` in shell or inside the script) guarantees the real API key is present, avoiding the masked `***` placeholder.
- No need to remember which Python binary to use; the pattern is always the same.

## Maintenance
- Keep the AgentMail SDK updated in the venv: `/opt/hermes/.venv/bin/uv pip install --upgrade agentmail`.
- If you change the location of the .env file, update the path in the script or cron source line.
- If you add other required packages, install them in the same venv.

## Troubleshooting
- **401/403 errors**: Verify that the API key loaded is the real key (starts with `am_us_`) and not the masked `***`. Print the first 8 chars for debugging.
- **ModuleNotFoundError**: Ensure you are using `/opt/hermes/.venv/bin/python`, not the system python.
- **Missing .env**: Confirm the file exists at the path you specify.

---
*This skill encapsulates the lesson learned: always pair the Hermes venv with a .env‑loaded API key when using AgentMail.*