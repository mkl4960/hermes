---
name: agentmail
description: Send emails using the AgentMail Python SDK
category: email
---
# AgentMail Email Skill

Send emails using the AgentMail Python SDK.

## Trigger Conditions
Use this skill when you need to:
- Send transactional or marketing emails via AgentMail API
- Automate email notifications from scripts or workflows
- Integrate email sending into Hermes Agent tasks

## Prerequisites
1. AgentMail Python SDK installed (should be available via `uv pip install agentmail`)
2. Valid AgentMail API key from [AgentMail.to](https://agentmail.to)
3. Basic Python knowledge

## Setup Steps

### 1. Install AgentMail (if not already installed)
```bash
uv pip install agentmail
```

### 2. Obtain API Key
- Sign up at [AgentMail.to](https://agentmail.to)
- Create an API key in the dashboard
- Keep the key secure (never commit to version control)

### 3. Configure Environment (Recommended)
Store your API key securely. Options:
- Environment variable: `AGENTMAIL_API_KEY=your_key_here`
- Python keyring or secure vault
- For testing, you can pass directly (not recommended for production)

### 4. Verify Installation
```python
import agentmail
print(agentmail.__version__)  # Should show 0.4.15 or later
```

## Sending an Email

### Basic Usage
```python
from agentmail import AgentMail

# Initialize client (reads AGENTMAIL_API_KEY from env by default)
client = AgentMail()

# Get your inbox ID (you'll have at least one)
inbox_id = client.inboxes.list().inboxes[0].inbox_id

# Send email
response = client.inboxes.messages.send(
    inbox_id=inbox_id,
    to=["recipient@example.com"],
    subject="Hello from AgentMail!",
    text="This is a test email sent via AgentMail SDK."
)

print(f"Email sent! Message ID: {response.message_id}")
```

### With HTML Content
```python
response = client.messages.send(
    to=["recipient@example.com"],
    subject="HTML Email",
    html="<h1>Hello</h1><p>This is <strong>HTML</strong> content.</p>",
    text="Hello\nThis is HTML content."  # Fallback for plaintext clients
)
```

### With CC, BCC, and Custom Headers
```python
response = client.messages.send(
    to=["to@example.com"],
    cc=["cc@example.com"],
    bcc=["bcc@example.com"],
    subject="Meeting Reminder",
    text="Don't forget our meeting tomorrow at 10 AM.",
    headers={"X-Priority": "high"}
)
```

## Advanced Features

### Using Templates
AgentMail supports templating with Handlebars syntax:
```python
response = client.messages.send(
    to=["user@example.com"],
    template_id="welcome_template",
    template_data={
        "name": "John",
        "product": "Awesome Tool"
    }
)
```

### Sending Attachments
```python
from agentmail.types import SendAttachment

response = client.messages.send(
    to=["recipient@example.com"],
    subject="Report Attached",
    text="Please find the monthly report attached.",
    attachments=[
        SendAttachment(
            content="base64_encoded_file_content",
            filename="report.pdf",
            content_type="application/pdf"
        )
    ]
)
```

## Verification
After sending:
1. Check response status: `response.status` should be `"sent"` or `"queued"`
2. Message ID: Save `response.id` for tracking
3. Dashboard: View sent emails in your AgentMail dashboard
4. Webhooks: Configure webhooks for delivery events

## Common Pitfalls & Solutions

### Pitfall: Authentication Error
**Error**: `401 Unauthorized` or `Invalid API key`
**Solution**: 
- Verify your API key is correct
- Ensure environment variable `AGENTMAIL_API_KEY` is set
- Check that the key hasn't expired or been revoked
- **Hermes-specific tip**: In the Hermes environment, API keys in `/opt/data/.env` may appear as `***` (masked) for security, but the actual values are available as environment variables. Access them directly from `os.environ` or ensure your shell sources the environment properly before running scripts. When in doubt, check the value with `echo $AGENTMAIL_API_KEY` in terminal.

### Pitfall: Rate Limiting
**Error**: `429 Too Many Requests`
**Solution**:
- Implement exponential backoff in your code
- Check your AgentMail plan limits
- Consider upgrading if you need higher volume

### Pitfall: Invalid Recipient
**Error**: `400 Bad Request` - invalid email address
**Solution**:
- Validate email addresses before sending
- Use regex or email validation libraries
- Check for typos in recipient addresses

## Example: Complete Script
Create `send_news_email.py`:
```python
#!/usr/bin/env python3
"""
Send BBC news headlines via AgentMail
"""
import os
from agentmail import AgentMail
from agentmail.types import SendAttachment

def main():
    # Initialize client
    client = AgentMail()
    
    # Email content (you would fetch this dynamically)
    news_content = """
    BBC NEWS HEADLINES - SATURDAY, APRIL 18, 2026
    ================================================
    
    TOP STORY:
    🚢 LIVE: Ships report attacks after Iran closes Strait of Hormuz
    The UK's maritime security authority reports incidents off Oman's coast as Tehran claims it closed the waterway in response to the continued US blockade of Iranian ports. Trump stated the US "won't be blackmailed."
    
    OTHER MAJOR HEADLINES:
    💼 BUSINESS (10 hours ago):
    What people in power think the impact of the Iran war will be
    Faisal Islam talks to some of the world's most powerful people about the conflict and the economy.
    
    🎪 CULTURE (16 hours ago):
    The Coachella campers taking their tents to the next extravagant level
    Campers are being judged for over-the-top tent setups at this year's festival in California.
    
    🌍 WORLD (6 hours ago):
    DR Congo accepts first set of deportees from the US
    The Congolese government stresses those expelled from the US are only in the country temporarily.
    
    🇪🇺 EUROPE (2 hours ago):
    Orbán's era was over in a flash and Hungary's next PM is a man in a hurry
    Péter Magyar and his Tisza party are wasting no time preparing for the transfer of power after their dramatic landslide victory.
    
    🇱🇧 MIDDLE EAST (37 minutes ago):
    French peacekeeper killed in southern Lebanon
    President Macron blames the attack on Hezbollah. The Iran-backed armed group denies any connection to the incident.
    
    🇫🇷 EUROPE (38 minutes ago):
    French film star Nathalie Baye dies aged 77
    President Macron said France had "loved, dreamed and grown up" with the stalwart of French cinema.
    """
    
    # Send email
    try:
        # Get inbox ID
        inbox_id = client.inboxes.list().inboxes[0].inbox_id
        
        response = client.inboxes.messages.send(
            inbox_id=inbox_id,
            to=["mkl4960@yahoo.com"],
            subject="Today's BBC News Headlines",
            text=news_content
        )
        print(f"✅ News email sent successfully! ID: {response.message_id}")
        return response.message_id
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise

if __name__ == "__main__":
    main()
```

Run it:
```bash
AGENTMAIL_API_KEY=your_key_here python send_news_email.py
```

## Maintenance
- Keep your AgentMail SDK updated: `uv pip install --upgrade agentmail`
- Monitor your AgentMail dashboard for usage and billing
- Rotate API keys periodically for security
- Test email sending in a staging environment before production use

## Troubleshooting
If emails aren't arriving:
1. Check spam/junk folders
2. Verify DNS records (SPF/DKIM/DMARC) are set up in AgentMail
3. Check AgentMail dashboard for delivery status
4. Ensure recipient address is valid and not blocked
5. Review any error logs from the AgentMail API response

## References
- AgentMail Documentation: https://docs.agentmail.to
- Python SDK Source: https://github.com/agentmail/to-python
- API Reference: https://docs.agentmail.to/reference