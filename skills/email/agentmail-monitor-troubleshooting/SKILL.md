---
name: agentmail-monitor-troubleshooting
description: Troubleshooting guide for the AgentMail monitor script when it produces no output.
---
# AgentMail Monitor Troubleshooting

## When to Use
When the AgentMail monitor script (`agentmail/monitor.py`) produces no output (silent) but you expect it to find new matching emails and extract YouTube URLs. This helps diagnose why the script isn't detecting new matches or extracting URLs.

## Prerequisites
- AgentMail Python SDK installed
- Access to the AgentMail inbox being monitored
- Persistent storage files (`seen_ids.txt`, `seen_urls.txt`) in `/opt/data/agentmail/`
- Environment variable `AGENTMAIL_API_KEY` set

## Steps

### 1. Verify Basic Script Execution
Run the monitor script directly to see if it produces any output or errors:
```bash
/opt/hermes/.venv/bin/python /opt/data/skills/email/agentmail-monitor/scripts/agentmail/monitor.py
```
If it exits silently (no output, exit code 0), proceed to debugging.

### 2. Check Environment and API Key
Ensure the API key is loaded:
```bash
env | grep AGENTMAIL
```
If missing, check that `/opt/data/.env` contains `AGENTMAIL_API_KEY=your_key`.

### 3. Examine the Monitor Script
Review the script to understand its logic:
```bash
cat /opt/data/skills/email/agentmail-monitor/scripts/agentmail/monitor.py
```
Key configuration:
- `TARGET_EMAIL`: email address to monitor
- `SEARCH_PHRASES`: list of phrases that must ALL be in the subject (case-insensitive)
- `SEEN_FILE`: tracks seen message IDs
- `SEEN_URLS_FILE`: tracks already-reported YouTube URLs

### 4. Verify Inbox Access
Create a debug script to confirm you can access the inbox and list messages:
```python
#!/opt/hermes/.venv/bin/python3
import os
from agentmail import AgentMail

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

client = AgentMail(api_key=os.environ.get('AGENTMAIL_API_KEY'))
target_email = 'laumiex@agentmail.to'  # or your target email
inbox_id = None
for inbox in client.inboxes.list().inboxes:
    if getattr(inbox, 'email', None) == target_email:
        inbox_id = inbox.inbox_id
        break

print(f"Inbox ID for {target_email}: {inbox_id}")
if inbox_id:
    messages_resp = client.inboxes.messages.list(inbox_id=inbox_id, limit=10)
    messages = getattr(messages_resp, 'messages', [])
    print(f"Found {len(messages)} recent messages")
    for msg in messages[:3]:
        print(f"  ID: {getattr(msg, 'message_id', None)}")
        print(f"  Subject: {getattr(msg, 'subject', '')}")
```

### 5. Check for Matching Subjects
Modify the debug script to check which messages match your search phrases:
```python
SEARCH_PHRASES = ['URL for', 'CLGNJ English Sunday Worship Service']  # from monitor.py
matches = []
for msg in messages:
    subject = getattr(msg, 'subject', '') or ''
    if msg_id := getattr(msg, 'message_id', None):
        if all(phrase.lower() in subject.lower() for phrase in SEARCH_PHRASES):
            matches.append((msg_id, subject))

print(f"Found {len(matches)} matching messages")
for msg_id, subject in matches:
    print(f"  MATCH: {msg_id} - {subject}")
```

### 6. Inspect Seen IDs
Check if matching message IDs have already been seen:
```bash
wc -l /opt/data/agentmail/seen_ids.txt
```
Load the seen IDs and compare with match IDs:
```python
SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, 'r') as f:
        seen_ids = set(line.strip() for line in f if line.strip())
else:
    seen_ids = set()

print(f"Loaded {len(seen_ids)} seen IDs")
match_ids = {msg_id for msg_id, _ in matches}
unseen_matches = [(msg_id, subject) for msg_id, subject in matches if msg_id not in seen_ids]
print(f"Unseen matches: {len(unseen_matches)}")
for msg_id, subject in unseen_matches:
    print(f"  {msg_id}: {subject}")
```

### 7. Extract YouTube URLs from Matches
For each unseen match, fetch the full message and extract YouTube URLs:
```python
import re

def extract_youtube_urls_from_text(text):
    if not text:
        return []
    youtube_pattern = r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|live/|embed/|v/|shorts/)[^\s<>\"\'\]+|https?://youtu\.be/[^\s<>\"\'\]+'
    return re.findall(youtube_pattern, text, re.IGNORECASE)

def extract_youtube_urls_from_html(html_text):
    if not html_text:
        return []
    href_pattern = r'href=[\'\"]([^\'\"]+)[\'\"]'
    src_pattern = r'src=[\'\"]([^\'\"]+)[\'\"]'
    href_matches = re.findall(href_pattern, html_text, re.IGNORECASE)
    src_matches = re.findall(src_pattern, html_text, re.IGNORECASE)
    all_potential_urls = href_matches + src_matches
    youtube_pattern = r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|live/|embed/|v/|shorts/)[^\s<>\"\'\]+|https?://youtu\.be/[^\s<>\"\'\]+'
    youtube_urls = []
    for url in all_potential_urls:
        if re.match(youtube_pattern, url, re.IGNORECASE):
            youtube_urls.append(url)
    return youtube_urls

def extract_youtube_urls(text, html_text=None):
    urls = []
    if text:
        urls.extend(extract_youtube_urls_from_text(text))
    if html_text:
        urls.extend(extract_youtube_urls_from_html(html_text))
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    return unique_urls

# For each unseen match:
for msg_id, subject in unseen_matches:
    try:
        msg_resp = client.inboxes.messages.get(inbox_id=inbox_id, message_id=msg_id)
        message = getattr(msg_resp, 'message', msg_resp)
        body = ''
        # Try common body attributes
        for attr in ['body', 'content', 'text', 'html']:
            if hasattr(message, attr):
                body = getattr(message, attr, '')
                if body:
                    break
        # Fallback to payload
        if not body and hasattr(message, 'payload'):
            payload = getattr(message, 'payload', '')
            if isinstance(payload, dict):
                body = payload.get('body', '') or payload.get('data', '')
            else:
                body = str(payload)
        
        print(f"Message {msg_id}: body length {len(body)}")
        urls = extract_youtube_urls(body)
        print(f"  Found {len(urls)} YouTube URLs: {urls}")
    except Exception as e:
        print(f"Error processing {msg_id}: {e}")
```

### 8. Check Seen URLs
Verify if extracted URLs have already been reported:
```bash
wc -l /opt/data/agentmail/seen_urls.txt
```
Compare new URLs against seen URLs.

### 9. Common Issues and Fixes
- **Script exits silently due to missing API key**: The monitor script checks for API key and returns silently if not found. Always verify with `env | grep AGENTMAIL`.
- **All matches already seen**: If monitoring has run before, all matching emails may be in `seen_ids.txt`. The script marks all fetched messages as seen (not just matches) to avoid reprocessing.
- **No YouTube URLs in body**: Even if subject matches, the body may not contain YouTube URLs. Check HTML parts as well as text.
- **Inbox ID lookup failure**: The script matches by `inbox.email` attribute. If that fails, it exits silently. Debug by printing inbox attributes.

### 10. Resetting State (Use with Caution)
To reprocess all messages as if never seen:
```bash
> /opt/data/agentmail/seen_ids.txt
> /opt/data/agentmail/seen_urls.txt
```
**Warning**: This will cause the monitor to report all historical matching URLs again.

### 11. Adding Debug Output to Monitor
Temporarily modify the monitor script to print debug info:
- Print number of messages fetched
- Print number of new matches found
- Print each match ID and subject
- Print extracted URLs before filtering
- Run with `python monitor.py` and observe output

## Verification
After fixing issues, run the monitor script and confirm it outputs new YouTube URLs (one per line) when new matching emails arrive.

## Related Skills
- `agentmail-monitor`: The original monitoring skill
- `agentmail-persistent-setup`: For setting up persistent storage
- `agentmail`: Basic AgentMail email sending/receiving

## References
- AgentMail Python SDK documentation
- Regex patterns for YouTube URL extraction
- File-based persistent storage patterns