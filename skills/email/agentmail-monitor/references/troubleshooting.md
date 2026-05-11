# AgentMail Monitor Troubleshooting Guide

## Common Issues and Solutions

### Issue: No Output / Silent Operation
**Symptoms**: 
- Script runs without errors but produces no output
- Cron job shows "ok" status but no notifications

**Diagnosis**:
- This is normal behavior - the script is designed to be silent when no NEW matches found
- Check that seen tracking files exist and are being updated
- Verify the script is actually running and checking your inbox

**Solution**:
1. Confirm script execution: Check cron job's last_run_at timestamp
2. Verify seen tracking: `ls -la /opt/data/agentmail/` should show seen_ids.txt and seen_urls.txt
3. Test manual run: `/opt/hermes/.venv/bin/python /opt/data/skills/email/agentmail-monitor/scripts/agentmail/monitor.py`
4. To force output for testing, reset tracking: `rm /opt/data/agentmail/seen_ids.txt /opt/data/agentmail/seen_urls.txt`

### Issue: Regex Syntax Errors
**Symptoms**:
- Script fails with "SyntaxError: unmatched ']'" or invalid escape sequence warnings
- Error occurs in YouTube URL pattern definitions

**Root Cause**:
- Complex regex patterns with nested escaping in raw strings
- Incorrect handling of quote characters in patterns

**Solution**:
Use simpler, tested patterns:
```python
# YouTube URL pattern that works reliably
youtube_pattern = r'https?://(?:www\.)?youtube\.com/(?:watch\?v=|live/|embed/|v/|shorts/)[^\s<>"\']+|https?://youtu\.be/[^\s<>"\']+'

# HTML attribute patterns
href_pattern = r'href=[\'"]([^\'"]+)[\'"]'
src_pattern = r'src=[\'"]([^\'"]+)[\'"]'
```

### Issue: Authentication Failures
**Symptoms**:
- Script exits silently (no output) due to missing API key
- AgentMail client initialization fails

**Diagnosis**:
- API key not available in environment when cron runs
- `.env` file not loaded properly

**Solution**:
1. Verify API key exists: `grep AGENTMAIL_API_KEY /opt/data/.env`
2. Ensure load_env_file() is called before AgentMail initialization
3. Check that the script loads `/opt/data/.env` explicitly
4. Test manual run to confirm authentication works

### Issue: Wrong Message ID Field
**Symptoms**:
- All messages treated as new (duplicate processing)
- OR all messages skipped (no matches found)
- seen_ids.txt grows incorrectly or not at all

**Root Cause**:
- Using `getattr(msg, 'id', None)` instead of `getattr(msg, 'message_id', None)`
- AgentMail message objects use `message_id` attribute, not `id`

**Solution**:
Always use the correct attribute:
```python
msg_id = getattr(msg, 'message_id', None)
# Never use: msg_id = getattr(msg, 'id', None)
```

### Issue: Case Sensitivity Problems
**Symptoms**:
- Emails with correct content are not matched
- Subject line matching fails intermittently

**Root Cause**:
- Exact case matching when subject lines vary in capitalization
- Phrases like "URL for" vs "url for" or "CLGNJ" vs "clgnj"

**Solution**:
Use case-insensitive matching:
```python
# Check subject contains both phrases (case-insensitive)
if all(phrase.lower() in subject.lower() for phrase in SEARCH_PHRASES):
```

### Issue: Missing YouTube URLs in HTML
**Symptoms**:
- Script detects matching emails but extracts zero YouTube URLs
- YouTube URLs are present in HTML `<a href>` tags but not found

**Root Cause**:
- Only scanning plain text fields (body, content, text, html)
- Not parsing HTML attributes for href/src values

**Solution**:
Implement proper HTML attribute parsing:
```python
def extract_youtube_urls_from_html(html_text):
    if not html_text:
        return []
    # Find href and src attributes
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
```

### Issue: Seen Tracking Not Persisting
**Symptoms**:
- seen_ids.txt and seen_urls.txt are reset or empty
- Script processes same emails repeatedly after container reload

**Root Cause**:
- Storage directory not persistent across container reloads
- Files being written to temporary location

**Solution**:
Ensure persistent storage is used:
- Store tracking files in `/opt/data/agentmail/` (not `/opt/hermes/` or `/tmp/`)
- Verify directory exists: `mkdir -p /opt/data/agentmail`
- Confirm script uses absolute paths to this directory

### Issue: Cron Job Using Wrong Script Path
**Symptoms**:\n- Cron job fails with "No such file or directory" error\n- Error shows path like `/opt/data/scripts/check_agentmail.py` doesn't exist\n\n**Root Cause**:\n- Outdated cron job configuration pointing to old/non-existent script\n- Skill-based script path not updated in cron job\n\n**Solution**:\nUpdate cron job to use current skill-based script:\n```bash\n*/10 * * * * /opt/hermes/.venv/bin/python /opt/data/skills/email/agentmail-monitor/scripts/monitor.py\n```\nUse `cronjob update` command with correct job_id and prompt.

### Issue: Hermes Virtual Environment Permission/Pip Problems
**Symptoms**:\n- Script fails with `ModuleNotFoundError: No module named 'agentmail'`\n- `/opt/hermes/.venv/bin/pip: No such file or directory`\n- `python3 -m pip install agentmail` fails with \"externally-managed-environment\" error\n- Virtual environment appears broken or incomplete\n\n**Root Cause**:\n- The Hermes virtual environment (`/opt/hermes/.venv`) may have permission issues, missing pip installation, or be improperly initialized\n- Running in container environments as non-root user can cause permission problems\n- Debian/Ubuntu systems have externally managed Python environments that block pip install system-wide\n\n**Solution**:\n1. **Use user site-packages with system Python** (recommended for Debian/Ubuntu):\n   ```bash\n   python3 -m pip install --break-system-packages agentmail\n   ```\n   This installs to `~/.local/lib/python3.13/site-packages` and is automatically on Python's path.\n\n2. **Create a dedicated virtual environment in writable location**:\n   ```bash\n   python3 -m venv /opt/data/venv\n   /opt/data/venv/bin/pip install agentmail\n   ```\n   Then ensure the monitor script uses `/opt/data/venv/bin/python` explicitly.\n\n3. **Fix Hermes venv permissions** (if you prefer to use it):\n   ```bash\n   # If you have sudo access\n   sudo chown -R $USER:$USER /opt/hermes/.venv\n   # Then try to reinstall pip\n   /opt/hermes/.venv/bin/python -m ensurepip --upgrade\n   ```\n\n4. **Verify the monitor script shebang**:\n   The script uses `#!/usr/bin/env python3`, so it will use whatever python3 is first in PATH.\n   Adjust your PATH or cron job to point to the correct Python if needed.\n\n**Verification**:\n- Test import: `python3 -c \"import agentmail; print('AgentMail version:', agentmail.__version__)\"`\n- Check that the monitoring script runs without import errors\n\n### Performance Optimization Tips

#### Batch Processing
- Process all messages in a single fetch (limit=50)
- Update seen set with ALL processed IDs, not just matches
- This prevents reprocessing the same messages in future runs

#### Efficient File I/O
- Load seen sets into memory at start
- Save to disk only after processing all messages
- Avoid opening/closing files in loops

#### Error Handling
- Wrap API calls in try/except to prevent cron job failures
- Silently exit on non-critical errors (no output for cron)
- Continue processing other messages if one fails

## Verification Checklist

When troubleshooting, verify:
1. [ ] Script runs successfully manually (exit code 0)
2. [ ] AgentMail API key is accessible in environment
3. [ ] Target inbox is found by email address
4. [ ] Recent messages are fetched (limit=50)
5. [ ] Message ID field is correctly accessed as `message_id`
6. [ ] Subject matching is case-insensitive
7. [ ] Seen tracking files are read and updated
8. [ ] YouTube URL patterns match your actual URLs
9. [ ] HTML attribute parsing works for href/src tags
10. [ ] Output only occurs for truly new, unseen matches

## When to Reset Tracking

Reset the seen tracking files when:
- You want to reprocess all historical emails as "new"
- Testing the monitoring functionality
- Seen files have become corrupted
- Changing monitoring criteria significantly

Command:
```bash
rm /opt/data/agentmail/seen_ids.txt /opt/data/agentmail/seen_urls.txt
```

## Log Monitoring

Since the script is silent when no new matches, monitor:
- Cron job status via `cronjob list` (look at last_run_at and last_status)
- Size/growth of seen tracking files over time
- Manual test runs to confirm functionality
- AgentMail API connectivity and rate limits