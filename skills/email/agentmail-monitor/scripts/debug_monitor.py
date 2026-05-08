#!/opt/hermes/.venv/bin/python3
import os
import sys
import re
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

SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'
SEEN_URLS_FILE = '/opt/data/agentmail/seen_urls.txt'
TARGET_EMAIL = 'laumiex@agentmail.to'
SEARCH_PHRASES = ['URL for', 'CLGNJ English Sunday Worship Service']

def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen(seen_set):
    with open(SEEN_FILE, 'w') as f:
        for msg_id in sorted(seen_set):
            f.write(msg_id + '\\n')

def load_seen_urls():
    if not os.path.exists(SEEN_URLS_FILE):
        return set()
    with open(SEEN_URLS_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def save_seen_urls(seen_urls_set):
    with open(SEEN_URLS_FILE, 'w') as f:
        for url in sorted(seen_urls_set):
            f.write(url + '\\n')

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

def main():
    print("Loading environment...")
    api_key = os.environ.get('AGENTMAIL_API_KEY')
    if not api_key:
        print("ERROR: No API key found")
        return
    print("API key found")

    client = AgentMail(api_key=api_key)
    target_email = TARGET_EMAIL
    inbox_id = None
    for inbox in client.inboxes.list().inboxes:
        if getattr(inbox, 'email', None) == target_email:
            inbox_id = inbox.inbox_id
            break
    if inbox_id is None:
        print(f"ERROR: No inbox found for {target_email}")
        return
    print(f"Found inbox ID: {inbox_id}")

    seen = load_seen()
    seen_urls = load_seen_urls()
    print(f"Loaded {len(seen)} seen message IDs")
    print(f"Loaded {len(seen_urls)} seen YouTube URLs")

    try:
        messages_resp = client.inboxes.messages.list(inbox_id=inbox_id, limit=50)
        messages = getattr(messages_resp, 'messages', [])
    except Exception as e:
        print(f"ERROR fetching messages: {e}")
        return
    print(f"Fetched {len(messages)} messages")

    new_matches = []
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        subject = getattr(msg, 'subject', '') or ''
        if msg_id is None:
            continue
        if msg_id in seen:
            continue
        if all(phrase.lower() in subject.lower() for phrase in SEARCH_PHRASES):
            new_matches.append((msg_id, subject))
            print(f"NEW MATCH: ID={msg_id}, Subject={subject}")

    print(f"Found {len(new_matches)} new matching messages")

    if not new_matches:
        print("No new matching messages - exiting")
        return

    # Update seen set with all processed IDs
    for msg in messages:
        msg_id = getattr(msg, 'message_id', None)
        if msg_id:
            seen.add(msg_id)
    print(f"Updated seen set to {len(seen)} IDs")
    save_seen(seen)

    youtube_urls = []
    for msg_id, subject in new_matches:
        try:
            msg_resp = client.inboxes.messages.get(inbox_id=inbox_id, message_id=msg_id)
            message = getattr(msg_resp, 'message', msg_resp)
            body = ''
            if hasattr(message, 'body'):
                body = getattr(message, 'body', '')
            elif hasattr(message, 'content'):
                body = getattr(message, 'content', '')
            elif hasattr(message, 'text'):
                body = getattr(message, 'text', '')
            elif hasattr(message, 'html'):
                body = getattr(message, 'html', '')
            if not body and hasattr(message, 'payload'):
                payload = getattr(message, 'payload', '')
                if isinstance(payload, dict):
                    body = payload.get('body', '') or payload.get('data', '')
                else:
                    body = str(payload)
            print(f"  Processing message {msg_id}: body length={len(body)}")
            urls = extract_youtube_urls(body)
            print(f"    Found {len(urls)} YouTube URLs: {urls}")
            youtube_urls.extend(urls)
        except Exception as e:
            print(f"  ERROR processing message {msg_id}: {e}")
            continue

    new_urls = [url for url in youtube_urls if url not in seen_urls]
    print(f"Found {len(new_urls)} new YouTube URLs: {new_urls}")
    seen_urls.update(new_urls)
    save_seen_urls(seen_urls)

    for url in new_urls:
        print(url)

if __name__ == '__main__':
    main()