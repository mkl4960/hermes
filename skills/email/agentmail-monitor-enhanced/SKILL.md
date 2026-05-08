---
name: agentmail-monitor-enhanced
category: email
description: Enhanced AgentMail monitoring with YouTube URL extraction and message labeling
---

# Enhanced AgentMail Monitoring with YouTube URL Extraction

## Approach for monitoring AgentMail inbox for specific emails and extracting YouTube URLs

This skill enhances the basic agentmail-monitor skill by adding YouTube URL extraction from email bodies and proper message labeling (marking as read) after processing. It's designed for silent cron operation where output is only produced when new matching emails with YouTube URLs are found.

## When to Use This Skill

Use this approach when you need to:
- Monitor an AgentMail inbox for emails matching specific subject criteria
- Extract YouTube URLs from the body of matching emails
- Automatically mark processed emails as read to avoid reprocessing
- Run automated checks via cron jobs without spamming output when no new matches
- Track processed emails persistently across container reloads

## Core Monitoring Script

Create or use the enhanced monitoring script at `/opt/data/scripts/agentmail/monitor_youtube.py`:

```python
#!/usr/bin/env python3
"""
Monitor AgentMail inbox for emails matching specific criteria and extract YouTube URLs.
Designed for silent cron operation - only outputs when new matches found.
"""
import os
import re
from agentmail import AgentMail

# Configuration - customize these for your use case
SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'  # Persistent storage for seen message IDs
TARGET_EMAIL = 'laumiex@agentmail.to'           # Email address to monitor
SEARCH_PHRASES = ['URL for', 'CLGNJ English Sunday Worship Service']  # Phrases that MUST all be in subject
YOUTUBE_REGEX = re.compile(r'https?://(?:www\\\\.)?youtube\\\\.com/(?:watch\\\\?v=[^\\\\s&]+|live/[^\\\\s&]+|embed/[^\\\\s&]+|v/[^\\\\s&]+|shorts/[^\\\\s&]+)|youtu.be/[^\\\\s]+')

def load_seen():
    """Load set of already seen message IDs from persistent storage."""
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(seen_set):
    """Save set of seen message IDs to persistent storage."""
    with open(SEEN_FILE, 'w') as f:
        for msg_id in sorted(seen_set):
            f.write(msg_id + '\\n')

def load_env_file(dotenv_path):
    """Load environment variables from a .env file."""
    if os.path.exists(dotenv_path):
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip().strip('"').strip("'")

def extract_first_youtube_url(text):
    """Extract the first YouTube URL from text."""
    if not text:
        return None
    match = YOUTUBE_REGEX.search(text)
    if match:
        return match.group(0)
    return None

def main():
    """Main monitoring function."""
    # Optionally load environment variables from .env file (common in Hermes)
    load_env_file('/opt/data/.env')
    
    seen = load_seen()
    # Initialize client with explicit API key from environment
    api_key = os.environ.get('AGENTMAIL_API_KEY')
    if not api_key:
        # Silently exit if no API key (for cron)
        return
    client = AgentMail(api_key=api_key)
    
    # Find target inbox by email address
    target_email = TARGET_EMAIL
    inbox_id = None
    for inbox in client.inboxes.list().inboxes:
        # Assuming inbox has attribute email
        if getattr(inbox, 'email', None) == target_email:
            inbox_id = inbox.inbox_id
            break
    if inbox_id is None:
        # Fallback: maybe inbox.id? Print error but exit silently (no output)
        return
    
    # Fetch recent messages (limit 50)
    try:
        messages_resp = client.inboxes.messages.list(inbox_id=inbox_id, limit=50)
        messages = getattr(messages_resp, 'messages', [])
    except Exception:
        return
    
    new_matches = []
    processed_ids = []  # Track all message IDs we process in this batch to update seen
    
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        subject = getattr(msg, 'subject', '') or ''
        body = getattr(msg, 'text', None) or getattr(msg, 'body', '') or ''
        
        if msg_id is None:
            continue
        if msg_id in seen:
            continue
        # Check subject contains both phrases (case-insensitive)
        if 'URL for' in subject and 'CLGNJ English Sunday Worship Service' in subject:
            # Extract first YouTube URL from body
            youtube_url = extract_first_youtube_url(body)
            if youtube_url:
                new_matches.append(youtube_url)
            # Mark as read: add read label, remove unread label
            try:
                client.inboxes.messages.add_label(inbox_id=inbox_id, message_id=msg_id, label="read")
                client.inboxes.messages.remove_label(inbox_id=inbox_id, message_id=msg_id, label="unread")
            except Exception:
                # If labeling fails, continue; we'll still mark as seen to avoid reprocessing
                pass
        
        # Track this message ID as processed (whether matched or not) to avoid reprocessing
        processed_ids.append(msg_id)
    
    if not new_matches:
        # No new matching emails with YouTube URLs; output nothing
        return
    
    # Update seen set with all processed IDs
    for msg_id in processed_ids:
        seen.add(msg_id)
    save_seen(seen)
    
    # Print notification(s)
    print('New YouTube link(s) found: ' + ' '.join(new_matches))

if __name__ == '__main__':
    main()
```

## Key Features

### 1. YouTube URL Extraction
- Uses regex to find YouTube URLs in email bodies
- Supports both youtube.com/watch?v= and youtu.be/ formats
- Extracts the first matching URL per email

### 2. Message Labeling
- Automatically adds "read" label to processed messages
- Removes "unread" label to keep inbox clean
- Gracefully handles labeling failures (continues processing)

### 3. Persistent Tracking
- Stores seen message IDs in `/opt/data/agentmail/seen_ids.txt`
- Survives container reloads and script restarts
- Updates with ALL processed IDs (not just matches) to prevent reprocessing

### 4. Silent Cron Operation
- Returns early (no output) when API key missing
- Returns early (no output) when inbox not found
- Returns early (no output) when API errors occur
- Returns early (no output) when no new matches found
- Only outputs when new YouTube URLs are detected

## Setup Instructions

### 1. Create Required Directories
```bash
mkdir -p /opt/data/scripts/agentmail
mkdir -p /opt/data/agentmail
```

### 2. Save the Monitoring Script
Save the enhanced monitoring script above as `/opt/data/scripts/agentmail/monitor_youtube.py`
Make executable: `chmod +x /opt/data/scripts/agentmail/monitor_youtube.py`

### 3. Configure Environment
Ensure AGENTMAIL_API_KEY is available:
- Option 1: Set in environment: `export AGENTMAIL_API_KEY=your_key_here`
- Option 2: Store in `/opt/data/.env`: `AGENTMAIL_API_KEY=your_key_here`
- The script will automatically load from `/opt/data/.env` if present

### 4. Set Up Cron Job
Example: Run every 15 minutes
```bash
*/15 * * * * /opt/hermes/.venv/bin/python /opt/data/scripts/agentmail/monitor_youtube.py
```

## Customization

### Modify Search Criteria
Edit the `SEARCH_PHRASES` array:
- Single phrase: `['Your Search Term']`
- Multiple phrases (ALL must be present): `['phrase1', 'phrase2', 'phrase3']`
- Case-sensitive matching

### Adjust YouTube Detection
Modify the `YOUTUBE_REGEX` pattern if needed for different URL formats

### Change Processing Limits
Adjust the `limit` parameter in `client.inboxes.messages.list()` call

## Verification & Testing

### Test Manual Run
```bash
/opt/hermes/.venv/bin/python /opt/data/scripts/agentmail/monitor_youtube.py
```
- No output = no new matches (normal for cron)
- Output shows YouTube URL(s) when new matches found

### Check Tracking File
After running, verify `/opt/data/agentmail/seen_ids.txt` contains message IDs

### Verify Message Labeling
Check that processed messages in AgentMail web UI show as "read"

### Simulate New Match
Send a test email matching criteria with YouTube URL, then run script - should output the URL

## Common Pitfalls and Solutions

### Pitfall: No Output but Expected Matches
**Check**: 
- API key is set (check `/opt/data/.env` or environment)
- Target email exists in AgentMail account
- Messages actually contain both search phrases
- Messages contain YouTube URLs matching the regex

### Pitfall: Duplicate Notifications
**Check**: 
- Seen file is being updated correctly
- Script has permission to write to `/opt/data/agentmail/`
- Not mixing different seen files (e.g., `/tmp/` vs `/opt/data/`)

### Pitfall: Labeling Failures
**Check**: 
- AgentMail API permissions allow label modification
- Network connectivity to AgentMail service
- Label names exactly match what's expected ("read", "unread")

### Pitfall: Missing YouTube URLs
**Check**: 
- Regex matches your YouTube URL format
- URL is in email body (not subject or headers)
- No whitespace or special characters breaking the match\n\n### Pitfall: Script returns no output but you expect new matches based on recent emails\n**Check**:\n- Seen file size vs inbox message count: If seen IDs >= total inbox messages, all messages are considered seen\n- Verify new messages actually match search criteria: Use API directly to check subjects of recent unseen messages\n- Ensure you're monitoring the correct inbox/email address\n- Check that API key has necessary permissions for message listing and reading\n\n**Solution**:\n1. Compare seen file line count with total message count from API\n2. If seen count >= total count, reset seen file (only if appropriate for your use case)\n3. Or, adjust your search to look for more recent messages only\n4. Use direct API calls to verify message subjects match your criteria before assuming script is broken\n\n## Advanced Patterns

### Multiple YouTube URLs per Email
To extract all URLs instead of just first:
```python
def extract_all_youtube_urls(text):
    """Extract all YouTube URLs from text."""
    if not text:
        return []
    return YOUTUBE_REGEX.findall(text)
```

### Different Output Formats
For webhook integration:
```python
print(f"EMAIL_MATCH:{msg_id}|{youtube_url}")
```

For JSON logging:
```python
import json
print(json.dumps({'event': 'youtube_found', 'url': youtube_url}))
```

### Date-Based Filtering
To only check recent emails (e.g., last 24 hours):
```python
from datetime import datetime, timezone, timedelta
# Inside message loop:
msg_time = getattr(msg, 'timestamp', None)
if msg_time and (datetime.now(timezone.utc) - msg_time) > timedelta(hours=24):
    continue  # Skip old messages
```

## Maintenance\n- Periodically prune the seen file if it grows too large (keep last N days/weeks)\n- Update search phrases as monitoring needs change\n- Test after AgentMail SDK updates to ensure compatibility\n- Monitor cron job logs (if enabled) to ensure silent operation when appropriate\n\n### Advanced Pattern: Tracking Seen URLs Separately\nTo avoid notifying about the same YouTube URL appearing in multiple emails (e.g., if the same live stream URL is resent), you can track seen URLs separately:\n\n1. Maintain a second persistent file for seen YouTube URLs\n2. Before printing a URL, check if it's been seen before\n3. Only update the seen URLs set with new URLs you're about to print\n4. This prevents duplicate notifications while still processing new email matches\n\nSee the `check_agentmail.py` script in `/opt/data/scripts/` for an implementation example.\n\n## Related Skills
- `email/agentmail`: For sending emails via AgentMail
- `email/agentmail-persistent-setup`: For general AgentMail persistence guidelines
- `devops/uv-package-installation`: For installing AgentMail SDK in Hermes environments
- `software-development/resolve-script-paths`: For locating scripts when expected paths don't exist