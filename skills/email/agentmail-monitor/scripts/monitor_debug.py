#!/opt/hermes/.venv/bin/python3
"""
Monitor AgentMail inbox for emails matching specific criteria.
Designed for silent cron operation - only outputs when new matches found.
"""
import os
import sys
import re
from agentmail import AgentMail

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
                cleaned_headers[key] = '\\\\'.join(c for c in value if ord(c) < 128)
            else:
                cleaned_headers[key] = value
        kwargs['headers'] = cleaned_headers
        return original_request(self, method, url, **kwargs)
    httpx.Client.request = patched_request
except Exception:
    # If patching fails, continue anyway
    pass

# Debug flag - set to True to see verbose output
DEBUG = True
def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


# Configuration - customize these for your use case
SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'  # Persistent storage for seen message IDs
SEEN_URLS_FILE = '/opt/data/agentmail/seen_urls.txt'  # Persistent storage for URLs already sent
TARGET_EMAIL = 'laumiex@agentmail.to'           # Email address to monitor
SEARCH_PHRASES = ['URL for', 'CLGNJ English Sunday Worship Service']  # Phrases that MUST all be in subject

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
            f.write(msg_id + '\n')

def load_seen_urls():
    """Load set of already seen YouTube URLs from persistent storage."""
    if not os.path.exists(SEEN_URLS_FILE):
        return set()
    with open(SEEN_URLS_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen_urls(seen_urls_set):
    """Save set of seen YouTube URLs to persistent storage."""
    with open(SEEN_URLS_FILE, 'w') as f:
        for url in sorted(seen_urls_set):
            f.write(url + '\n')

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

def extract_youtube_urls_from_text(text):
    """Extract YouTube URLs from plain text."""
    if not text:
        return []
    # Pattern for YouTube URLs: covers watch, live, embed, v, shorts, and youtu.be formats
    # Allow any characters except spaces, <, >, ", '\n
    youtube_pattern = r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|live/|embed/|v/|shorts/)[^\s<>"\']+|https?://youtu\.be/[^\s<>"\']+'
    return re.findall(youtube_pattern, text, re.IGNORECASE)

def extract_youtube_urls_from_html(html_text):
    """Extract YouTube URLs from HTML by parsing href/src attributes."""
    if not html_text:
        return []
    # Find href and src attributes using regex that handles quotes properly
    href_pattern = r'href=[\'\"]([^\'\"]+)[\'\"]'
    src_pattern = r'src=[\'\"]([^\'\"]+)[\'\"]'
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
    # Optionally load environment variables from .env file (common in Hermes)
    load_env_file('/opt/data/.env')
    debug_print('Loaded environment from .env')
    seen = load_seen()
    seen_urls = load_seen_urls()
    debug_print('Loaded {} seen IDs, {} seen URLs'.format(len(seen), len(seen_urls)))
    # Initialize client with explicit API key from environment
    api_key = os.environ.get('AGENTMAIL_API_KEY')
    if api_key:
        debug_print('API key found (length {})'.format(len(api_key)))
    else:
        debug_print('API key NOT found')
        # Silently exit if no API key (for cron)
        return
    client = AgentMail(api_key=api_key)
    
    # Find target inbox by email address
    target_email = TARGET_EMAIL
    inbox_id = None
    try:
        inboxes_response = client.inboxes.list()
    except (UnicodeEncodeError, Exception):
        # Silently fail if there's an issue listing inboxes (e.g., Unicode headers)
        return
    # Find target inbox by email address
    for inbox in getattr(inboxes_response, "inboxes", []):
        # Assuming inbox has attribute email
        if getattr(inbox, "email", None) == target_email:
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
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        subject = getattr(msg, 'subject', '') or ''
        if msg_id is None:
            continue
        if msg_id in seen:
            continue
        # Check subject contains both phrases (case-insensitive)
        if all(phrase.lower() in subject.lower() for phrase in SEARCH_PHRASES):
            new_matches.append((msg_id, subject))
    
    if not new_matches:
        # No new matching emails; output nothing
        return
    
    # Update seen set with all processed IDs (including non-matching messages)
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        if msg_id:
            seen.add(msg_id)
    save_seen(seen)
    
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
                body = getattr(message, 'body', '')
            elif hasattr(message, 'content'):
                body = getattr(message, 'content', '')
            elif hasattr(message, 'text'):
                body = getattr(message, 'text', '')
            elif hasattr(message, 'html'):
                body = getattr(message, 'html', '')
            # If still empty, try to get from a 'payload' or 'parts' (common in email APIs)
            if not body and hasattr(message, 'payload'):
                payload = getattr(message, 'payload', '')
                if isinstance(payload, dict):
                    body = payload.get('body', '') or payload.get('data', '')
                else:
                    body = str(payload)
            
            # Extract YouTube URLs from body
            urls = extract_youtube_urls(body)
            youtube_urls.extend(urls)
        except Exception:
            # If we fail to get the message or extract, skip this message
            continue
    
    # Filter out URLs we've already seen
    new_urls = [url for url in youtube_urls if url not in seen_urls]
    # Update seen URLs with the new ones we're about to print
    seen_urls.update(new_urls)
    save_seen_urls(seen_urls)
    
    # Print YouTube URLs found (one per line)
    for url in new_urls:
        print(url)

if __name__ == '__main__':
    main()