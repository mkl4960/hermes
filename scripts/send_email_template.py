#!/opt/hermes/.venv/bin/python3
"""
Generic AgentMail email sender template.

- Uses the Hermes virtual environment (/opt/hermes/.venv/bin/python)
- Loads API key from a .env file (default /opt/data/.env)
- Provides a reusable send_email() function
- Intended to be copied/customized for specific email tasks.

Usage:
    1. Copy this template to a new script (e.g., send_weather_email.py).
    2. Edit the `build_message()` function to create your subject and body.
    3. Optionally adjust the .env path or recipient list.
    4. Run: /opt/hermes/.venv/bin/python /path/to/your_script.py
       Or, if you have sourced the .env: source /opt/data/.env && /opt/hermes/.venv/bin/python /path/to/your_script.py
"""

import os
import json
import urllib.request  # example import; adjust as needed
from agentmail import AgentMail


def load_dotenv(env_path: str = "/opt/data/.env") -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ.
    Existing environment variables are not overwritten.
    """
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Only set if not already in environment (respect existing exports)
                if key not in os.environ:
                    os.environ[key] = value


def get_tomorrow_weather(city: str) -> str:
    """Example helper: fetches tomorrow's weather from wttr.in."""
    url = f"https://wttr.in/{city}?format=j1"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
    tomorrow = data["weather"][1]  # index 0 = today, 1 = tomorrow
    hourly = tomorrow["hourly"]
    noon = next((h for h in hourly if h["time"] == "1200"), hourly[0])
    condition = noon["weatherDesc"][0]["value"]
    mintemp = tomorrow["mintempC"]
    maxtemp = tomorrow["maxtempC"]
    wind = noon["windspeedKmph"]
    humidity = noon["humidity"]
    return f"{condition}, {mintemp}-{maxtemp}°C, wind {wind}km/h, humidity {humidity}%"


def build_message() -> tuple[str, str]:
    """Build the email subject and body.
    Customize this function for your specific email content.
    Returns:
        (subject, body)
    """
    # Example: weather + dryer troubleshooting (feel free to replace)
    weather = get_tomorrow_weather("Boston")
    body = f"""Boston tomorrow: {weather}

Dryer Heats but Won't Spin – Troubleshooting Steps:

1. Safety: Unplug dryer.
2. Quick checks: Door switch clicks? Start button hums? Drum turns freely by hand?
3. Access drive‑train: Remove lint screen, top panel, front panel.
4. Inspect drive belt for cracks, looseness, or breakage; replace if needed.
5. Check drum rollers & axles for wear; replace if noisy or wobbly.
6. Examine idler pulley for smooth rotation; replace if damaged.
7. Test motor: With belt off, motor should run smoothly; humming but no turn may indicate seized motor or bad capacitor.
8. Verify thermal fuse continuity; replace if open.
9. Reassemble and test on air‑fluff cycle.
10. Call pro for motor/control‑board issues.

Quick checklist:
[ ] Unplug
[ ] Door switch OK
[ ] Belt intact
[ ] Rollers spin free
[ ] Idler pulley turns
[ ] Motor runs (belt off)
[ ] Thermal fuse continuity
[ ] Reassemble & test
"""
    subject = "Boston Weather Tomorrow & Dryer Troubleshooting Guide"
    return subject, body


def send_email(
    to: list[str],
    subject: str,
    body: str,
    env_path: str = "/opt/data/.env",
) -> None:
    """Send an email via AgentMail.
    Args:
        to: List of recipient email addresses.
        subject: Email subject line.
        body: Email plain‑text body.
        env_path: Path to .env file containing AGENTMAIL_API_KEY.
    """
    # Load environment (ensures API key is available)
    load_dotenv(env_path)

    # Initialize AgentMail client (reads AGENTMAIL_API_KEY from os.environ)
    client = AgentMail()

    # Get the default inbox ID
    inbox_id = client.inboxes.list().inboxes[0].inbox_id

    # Send the email
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=to,
        subject=subject,
        text=body,
    )
    print(f"Email sent! ID: {response.message_id}")


def main() -> None:
    """Example entry point – customize as needed."""
    # Load .env (optional, also done inside send_email)
    load_dotenv()

    # Build message
    subject, body = build_message()

    # Define recipients
    recipients = ["mkl4960@yahoo.com"]  # <-- change as needed

    # Send
    send_email(to=recipients, subject=subject, body=body)


if __name__ == "__main__":
    main()