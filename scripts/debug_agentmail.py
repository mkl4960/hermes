#!/usr/bin/env python3
import os
from agentmail import AgentMail

api_key = os.environ.get('AGENTMAIL_API_KEY')
client = AgentMail(api_key=api_key)

print("AgentMail object attributes:")
for attr in sorted(dir(client)):
    if not attr.startswith('_'):
        print(f"  {attr}")

print("\nChecking for messages attribute:")
if hasattr(client, 'messages'):
    print("  client.messages exists")
    print(f"  Type: {type(client.messages)}")
else:
    print("  client.messages does NOT exist")

print("\nChecking for inboxes attribute:")
if hasattr(client, 'inboxes'):
    print("  client.inboxes exists")
    print(f"  Type: {type(client.inboxes)}")
    if hasattr(client.inboxes, 'messages'):
        print("  client.inboxes.messages exists")
        print(f"  Type: {type(client.inboxes.messages)}")
    else:
        print("  client.inboxes.messages does NOT exist")
else:
    print("  client.inboxes does NOT exist")