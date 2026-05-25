#!/usr/bin/env python3
"""
Monitor AgentMail inbox for emails matching specific criteria and extract YouTube URL from body.
Designed for silent cron operation - only outputs YouTube URL when new match found.
"""
import os
import re
from agentmail import AgentMail

# Configuration - customize these for your use case
SEEN_FILE = '/opt/data/agentmail/clg_youtube_link_seen_ids.txt'  # Persistent storage for seen message IDs
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

def extract_youtube_url(text):
    """Extract YouTube URL from text using regex."""
    # Pattern to match YouTube URLs
    youtube_pattern = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s&]+)'
    match = re.search(youtube_pattern, text)
    if match:
        return match.group(1)
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
    
    youtube_urls = []
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        subject = getattr(msg, 'subject', '') or ''
        if msg_id is None:
            continue
        if msg_id in seen:
            continue
        # Check subject contains both phrases (case-insensitive)
        if 'URL for' in subject and 'CLGNJ English Sunday Worship Service' in subject:
            # Fetch full message to get body
            try:
                full_msg = client.inboxes.messages.get(inbox_id=inbox_id, message_id=msg_id)
                body = getattr(full_msg, 'text', '') or getattr(full_msg, 'body', '') or ''
                url = extract_youtube_url(body)
                if url:
                    youtube_urls.append(url)
            except Exception:
                # If we can't fetch the message, skip URL extraction but still mark as seen
                pass
    
    if not youtube_urls:
        # No new matching emails with YouTube URL; output nothing
        return
    
    # Update seen set with all processed IDs
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        if msg_id:
            seen.add(msg_id)
    save_seen(seen)
    
    # Print YouTube URL(s) - one per line
    for url in youtube_urls:
        print(url)

if __name__ == '__main__':
    main()