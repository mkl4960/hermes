#!/usr/bin/env python3
import os
from agentmail import AgentMail

api_key = os.environ.get('AGENTMAIL_API_KEY')
print(f"API key present: {bool(api_key)}")
if api_key:
    print(f"API key first 10 chars: {api_key[:10]}")
else:
    print("API key is empty or not set")

client = AgentMail(api_key=api_key)
try:
    inboxes = client.inboxes.list()
    print(f"Successfully listed inboxes: {len(inboxes.inboxes)} inboxes")
    for ib in inboxes.inboxes:
        print(f"  - {ib.email} (id: {ib.inbox_id})")
    inbox_id = inboxes.inboxes[0].inbox_id
    print(f"Using inbox ID: {inbox_id}")
except Exception as e:
    print(f"Error listing inboxes: {e}")
    # Try fallback
    inbox_id = 'laumiex@agentmail.to'
    print(f"Using fallback inbox ID: {inbox_id}")

# Now try to send a test email
try:
    response = client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=['mkl4960@gmail.com'],
        subject='Test from isolated script',
        text='This is a test email.'
    )
    print(f"Email sent successfully! ID: {response.message_id}")
except Exception as e:
    print(f"Error sending email: {e}")