#!/usr/bin/env python3
"""
Monitor AgentMail inbox for emails matching specific criteria.
Designed for silent cron operation - only outputs when new matches found.
Logs operational details to /opt/data/agentmail/monitor.log for debugging.
"""
import os
import sys
import re
import datetime
# Add user site-packages to path for agentmail import
sys.path.insert(0, '/opt/data/home/.local/lib/python3.13/site-packages')
from agentmail import AgentMail

LOG_FILE = '/opt/data/agentmail/monitor.log'

def log_message(msg):
    """Append a timestamped message to the log file."""
    try:
        with open(LOG_FILE, 'a') as f:
            f.write('[{}] {}\n'.format(datetime.datetime.now().isoformat(), msg))
    except Exception:
        # If logging fails, we don't want to break the monitor
        pass

# Patch httpx to handle non-ASCII characters in headers (e.g., User-Agent)
try:
    import httpx
    original_request = httpx.Client.request
    def patched_request(self, method, url, **kwargs):
        headers = kwargs.get('headers', {})
        # Remove non-ASCII characters from all header values to avoid UnicodeEncodeError
        # HTTP headers must be ASCII according to RFC 7230
        cleaned_headers = {}
        for key, value in headers.items():
            if isinstance(value, str):
                cleaned_headers[key] = ''.join(c for c in value if ord(c) < 128)
            else:
                cleaned_headers[key] = value
        kwargs['headers'] = cleaned_headers
        return original_request(self, method, url, **kwargs)
    httpx.Client.request = patched_request
except Exception:
    # If patching fails, continue anyway
    pass

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

def load_seen():
    """Load set of already seen message IDs from persistent storage."""
    SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(seen_set):
    """Save set of seen message IDs to persistent storage."""
    SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'
    with open(SEEN_FILE, 'w') as f:
        for msg_id in sorted(seen_set):
            f.write(msg_id + '\n')

def load_seen_urls():
    """Load set of already seen YouTube URLs from persistent storage."""
    SEEN_URLS_FILE = '/opt/data/agentmail/seen_urls.txt'
    if not os.path.exists(SEEN_URLS_FILE):
        return set()
    with open(SEEN_URLS_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen_urls(seen_urls_set):
    """Save set of seen YouTube URLs to persistent storage."""
    SEEN_URLS_FILE = '/opt/data/agentmail/seen_urls.txt'
    with open(SEEN_URLS_FILE, 'w') as f:
        for url in sorted(seen_urls_set):
            f.write(url + '\n')

def extract_youtube_urls_from_text(text):
    """Extract YouTube URLs from plain text."""
    if not text:
        return []
    # Pattern for YouTube URLs: covers watch, live, embed, v, shorts, and youtu.be formats
    # Allow any characters except spaces, <, >, ", '
    youtube_pattern = r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|live/|embed/|v/|shorts/)[^\s<>"\']+|https?://youtu\.be/[^\s<>"\']+'
    return re.findall(youtube_pattern, text, re.IGNORECASE)

def extract_youtube_urls_from_html(html_text):
    """Extract YouTube URLs from HTML by parsing href/src attributes."""
    if not html_text:
        return []
    # Find href and src attributes using regex that handles quotes properly
    href_pattern = r'href=[\'"]([^\'"]+)[\'"]'
    src_pattern = r'src=[\'"]([^\'"]+)[\'"]'
    href_matches = re.findall(href_pattern, html_text, re.IGNORECASE)
    src_matches = re.findall(src_pattern, html_text, re.IGNORECASE)
    all_potential_urls = href_matches + src_matches

    # Filter for YouTube URLs
    youtube_pattern = r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|live/|embed/|v/|shorts/)[^\s<>"\']+|https?://youtu\.be/[^\s<>"\']+'
    youtube_urls = []
    for url in all_potential_urls:
        if re.match(youtube_pattern, url, re.IGNORECASE):
            youtube_urls.append(url)
    return youtube_urls

def extract_youtube_urls(text, html_text=None):
    """Extract YouTube URLs from text and/or HTML."""
    urls = []
    if text:
        urls.extend(extract_youtube_urls_from_text(text))
    if html_text:
        urls.extend(extract_youtube_urls_from_html(html_text))
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    return unique_urls

def main():
    """Main monitoring function."""
    log_message('=== AgentMail monitor started ===')
    # Optionally load environment variables from .env file (common in Hermes)
    load_env_file('/opt/data/.env')
    log_message('Loaded environment from .env')
    
    seen = load_seen()
    seen_urls = load_seen_urls()
    log_message('Loaded {} seen IDs, {} seen URLs'.format(len(seen), len(seen_urls)))
    
    # Initialize client with explicit API key from environment
    api_key = os.environ.get('AGENTMAIL_API_KEY')
    if not api_key:
        log_message('API key NOT found - exiting')
        # Silently exit if no API key (for cron)
        return
    log_message('API key found (length {})'.format(len(api_key)))
    try:
        client = AgentMail(api_key=api_key)
        log_message('AgentMail client initialized')
    except Exception as e:
        log_message('Failed to initialize AgentMail client: {}'.format(e))
        return
    
    # Find target inbox by email address
    target_email = 'laumiex@agentmail.to'
    inbox_id = None
    try:
        inboxes_response = client.inboxes.list()
        log_message('Successfully listed inboxes')
    except Exception as e:
        log_message('Error listing inboxes: {}'.format(e))
        return
    # Find target inbox by email address
    for inbox in getattr(inboxes_response, 'inboxes', []):
        # Assuming inbox has attribute email
        if getattr(inbox, 'email', None) == target_email:
            inbox_id = inbox.inbox_id
            break
    if inbox_id is None:
        log_message('Target inbox not found for email: {}'.format(target_email))
        # Fallback: maybe inbox.id? Print error but exit silently (no output)
        return
    log_message('Target inbox ID: {}'.format(inbox_id))
    
    # Fetch recent messages (limit 50)
    try:
        messages_resp = client.inboxes.messages.list(inbox_id=inbox_id, limit=50)
        messages = getattr(messages_resp, 'messages', [])
        log_message('Fetched {} messages'.format(len(messages)))
    except Exception as e:
        log_message('Error listing messages: {}'.format(e))
        return
    
    new_matches = []
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        subject = getattr(msg, 'subject', '') or ''
        if msg_id is None:
            continue
        if msg_id in seen:
            continue
        # Check subject contains both phrases (case-insensitive)
        if all(phrase.lower() in subject.lower() for phrase in ['URL for', 'CLGNJ English Sunday Worship Service']):
            new_matches.append((msg_id, subject))
            log_message('New match found: ID={}, Subject={}'.format(msg_id, subject))
        else:
            # Log non-matching subjects that contain 'URL for' for debugging
            if 'URL for' in subject:
                log_message('Subject contains URL for but not both phrases: {}'.format(subject))
    
    log_message('Total new matches: {}'.format(len(new_matches)))
    
    if not new_matches:
        log_message('No new matching emails - exiting')
        # No new matching emails; output nothing
        return
    
    # Update seen set with all processed IDs (including non-matching messages)
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        if msg_id:
            seen.add(msg_id)
    save_seen(seen)
    log_message('Updated seen IDs, now {} seen'.format(len(seen)))
    
    # Process each new matching email to extract YouTube URL
    youtube_urls = []
    for msg_id, subject in new_matches:
        try:
            # Fetch full message to get body
            msg_resp = client.inboxes.messages.get(inbox_id=inbox_id, message_id=msg_id)
            # Assuming the response has a 'message' attribute or is the message itself
            message = getattr(msg_resp, 'message', msg_resp)
            # Extract body - try common attributes
            body = ''
            if hasattr(message, 'body'):
                val = getattr(message, 'body')
                body = val if val is not None else ''
            elif hasattr(message, 'content'):
                val = getattr(message, 'content')
                body = val if val is not None else ''
            elif hasattr(message, 'text'):
                val = getattr(message, 'text')
                body = val if val is not None else ''
            elif hasattr(message, 'html'):
                val = getattr(message, 'html')
                body = val if val is not None else ''
            # If still empty, try to get from a 'payload' or 'parts' (common in email APIs)
            if not body and hasattr(message, 'payload'):
                payload = getattr(message, 'payload')
                if isinstance(payload, dict):
                    body = payload.get('body', '') or payload.get('data', '')
                    if body is None:
                        body = ''
                else:
                    if payload is not None:
                        body = str(payload)
                    else:
                        body = ''
            log_message('Processing message ID={}, body length={}'.format(msg_id, len(body)))
            urls = extract_youtube_urls(body)
            log_message('Extracted URLs: {}'.format(urls))
            youtube_urls.extend(urls)
        except Exception as e:
            log_message('Error processing message {}: {}'.format(msg_id, e))
            # If we fail to get the message or extract, skip this message
            continue
    
    # Filter out URLs we've already seen
    new_urls = [url for url in youtube_urls if url not in seen_urls]
    log_message('New YouTube URLs to send: {}'.format(new_urls))
    # Update seen URLs with the new ones we're about to print
    seen_urls.update(new_urls)
    save_seen_urls(seen_urls)
    log_message('Updated seen URLs, now {} seen'.format(len(seen_urls)))
    
    # Print YouTube URLs found (one per line) - this output is captured by cron for delivery
    for url in new_urls:
        print(url)
    
    log_message('=== AgentMail monitor finished ===')

if __name__ == '__main__':
    main()