#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error

api_key = os.environ.get('AGENTMAIL_API_KEY')
if not api_key:
    print("API key not set")
    exit(1)

# Try to list inboxes via GET
url = "https://api.agentmail.to/inboxes"
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {api_key}')
req.add_header('Content-Type', 'application/json')

try:
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
        print("List inboxes success:")
        print(json.dumps(data, indent=2))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(e.read().decode())
except Exception as e:
    print(f"Error: {e}")