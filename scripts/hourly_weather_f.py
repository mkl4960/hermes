import os
import json
import urllib.request
import urllib.error
import sys
import time
sys.path.insert(0, '/opt/data/agentmail_packages')
from agentmail import AgentMail

def fetch_weather_json(city, retries=3, backoff_factor=1):
    url = f'https://wttr.in/{city}?format=j1'
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url) as resp:
                return json.load(resp)
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(backoff_factor * (2 ** attempt))
            else:
                raise

def format_hourly(hourly_list):
    lines = []
    for hour in hourly_list:
        time = hour['time']  # like '000', '0300', etc.
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
        precipmm = hour['precipMM']  # mm, could convert to inches but keep mm
        lines.append(f"{time_str} | {condition:20} | {tempf}°F (feels {feelslikef}°F) | wind {windmph}mph {winddir} | humidity {humidity}% | precip {precipmm}mm")
    return "\n".join(lines)

def main():
    boston_data = fetch_weather_json('Boston')
    parsippany_data = fetch_weather_json('Parsippany')
    boston_hourly = boston_data['weather'][0]['hourly']  # Changed from [1] to [0] for today
    parsippany_hourly = parsippany_data['weather'][0]['hourly']  # Changed from [1] to [0] for today
    
    boston_section = f"Boston (today):\n" + format_hourly(boston_hourly)  # Changed from (tomorrow) to (today)
    parsippany_section = f"Parsippany (today):\n" + format_hourly(parsippany_hourly)  # Changed from (tomorrow) to (today)
    
    body = f"""Hi,

Here is the hour-by-hour weather forecast for today in Fahrenheit:

{boston_section}

{parsippany_section}

Stay dry!

"""
    client = AgentMail()
    inbox_id = client.inboxes.list().inboxes[0].inbox_id
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=["mkl4960@yahoo.com"],
        subject="Hour-by-hour Weather Forecast for Today (°F)",  # Changed from Tomorrow to Today
        text=body
    )
    print(f"Email sent! ID: {response.message_id}")

if __name__ == "__main__":
    main()