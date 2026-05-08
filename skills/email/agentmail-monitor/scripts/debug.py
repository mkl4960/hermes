#!/opt/hermes/.venv/bin/python3
import os
import sys
from agentmail import AgentMail

# Load environment variables from .env file
def load_env_file(dotenv_path):
    if os.path.exists(dotenv_path):
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip().strip('"').strip("'")

load_env_file('/opt/data/.env')

api_key = os.environ.get('AGENTMAIL_API_KEY')
if not api_key:
    print("No API key found")
    sys.exit(1)

client = AgentMail(api_key=api_key)

target_email = 'laumiex@agentmail.to'
inbox_id = None
for inbox in client.inboxes.list().inboxes:
    if getattr(inbox, 'email', None) == target_email:
        inbox_id = inbox.inbox_id
        break

if inbox_id is None:
    print(f"No inbox found for {target_email}")
    sys.exit(1)

print(f"Found inbox ID: {inbox_id}")

# Fetch recent messages (limit 50)
messages_resp = client.inboxes.messages.list(inbox_id=inbox_id, limit=50)
messages = getattr(messages_resp, 'messages', [])
print(f"Found {len(messages)} messages")

for msg in messages[:5]:  # Just show first 5
    msg_id = getattr(msg, 'message_id', None)
    subject = getattr(msg, 'subject', '') or ''
    print(f"  ID: {msg_id}, Subject: {subject}")