#!/usr/bin/env python3
import os
from agentmail import AgentMail

api_key = os.environ.get('AGENTMAIL_API_KEY')
if not api_key:
    print("API key not set")
    exit(1)

client = AgentMail(api_key=api_key)
try:
    inboxes = client.inboxes.list()
    inbox_id = inboxes.inboxes[0].inbox_id
    print(f"Got inbox ID: {inbox_id}")
except Exception as e:
    print(f"Error listing inboxes: {e}")
    exit(1)

try:
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=['mkl4960@gmail.com'],
        subject='Test email',
        text='This is a test.'
    )
    print(f"Email sent! ID: {response.message_id}")
except Exception as e:
    print(f"Error sending email: {e}")
    exit(1)