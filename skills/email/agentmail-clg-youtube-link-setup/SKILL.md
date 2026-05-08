---
name: agentmail-clg-youtube-link-setup
description: Procedure for renaming AgentMail persistent storage files to use clg_youtube_link_ prefix
---

# AgentMail Persistent Files Renaming to clg_youtube_link_ Prefix

## Purpose
This skill provides a procedure for renaming AgentMail persistent storage files (seen IDs and seen URLs) to use the `clg_youtube_link_` prefix while maintaining the original `agentmail` directory structure. This is useful when integrating AgentMail with YouTube monitoring or other specific use cases requiring custom file naming conventions.

## When to Use
- When you need to change the prefix of AgentMail seen files from the default (e.g., `agentmail_seen*.txt`) to a custom prefix like `clg_youtube_link_`
- When setting up or modifying AgentMail integrations that require specific file naming for clarity or organization
- After container reloads when persistent files need to be renamed to match updated script references

## Prerequisites
- AgentMail integration already set up (refer to `agentmail-persistent-setup` skill)
- Access to `/opt/data/agentmail/` directory for persistent storage
- Access to `/opt/data/scripts/agentmail/` directory for monitoring scripts
- Basic file manipulation and text editing capabilities

## Procedure

### 1. Identify Current Persistent Files
Locate the existing AgentMail seen files in the persistent storage directory:
```bash
ls -la /opt/data/agentmail/
```
Typical files to rename:
- `seen_ids.txt` (stores seen message IDs)
- `seen_urls.txt` (stores seen YouTube URLs or other tracked URLs)

### 2. Rename Persistent Files
Rename the files to use the `clg_youtube_link_` prefix:
```bash
mv /opt/data/agentmail/seen_ids.txt /opt/data/agentmail/clg_youtube_link_seen_ids.txt
mv /opt/data/agentmail/seen_urls.txt /opt/data/agentmail/clg_youtube_link_seen_urls.txt
```

### 3. Update Monitoring Scripts
Edit any AgentMail monitoring scripts to reference the new file paths. For example, in a YouTube monitoring script:

**Before:**
```python
SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'
SEEN_URLS_FILE = '/opt/data/agentmail/seen_urls.txt'
```

**After:**
```python
SEEN_FILE = '/opt/data/agentmail/clg_youtube_link_seen_ids.txt'
SEEN_URLS_FILE = '/opt/data/agentmail/clg_youtube_link_seen_urls.txt'
```

### 4. Verify Changes
Confirm the renaming and script updates:
```bash
ls -la /opt/data/agentmail/
# Should show clg_youtube_link_seen_ids.txt and clg_youtube_link_seen_urls.txt

# Check that the script references the new paths
grep -n \"clg_youtube_link\" /opt/data/scripts/agentmail/monitor_youtube.py
```

### 5. Test the Integration
Run the monitoring script manually to ensure it works with the new file names:
```bash
python3 /opt/data/scripts/agentmail/monitor_youtube.py
```
Verify that new message IDs and URLs are being stored in the renamed files.

## Pitfalls & Troubleshooting
- **Script still referencing old paths**: Double-check all scripts in `/opt/data/scripts/agentmail/` for hardcoded paths to the old file names.
- **Permission issues**: Ensure the user running the script has read/write access to the `/opt/data/agentmail/` directory.
- **Container reloads**: Remember that `/opt/data/` persists across container reloads, so renamed files will remain unless explicitly deleted or moved.
- **Multiple integrations**: If running multiple AgentMail integrations, ensure each uses distinct file prefixes to avoid conflicts.

## Verification
- The persistent files `/opt/data/agentmail/clg_youtube_link_seen_ids.txt` and `/opt/data/agentmail/clg_youtube_link_seen_urls.txt` exist and are being updated by the monitoring script.
- The monitoring script runs without errors and correctly tracks seen messages and URLs.
- No files with the old names (`seen_ids.txt`, `seen_urls.txt`) remain in `/opt/data/agentmail/` (unless intentionally kept for backup).

## Related Skills
- `agentmail-persistent-setup`: Initial setup of AgentMail persistent storage
- `agentmail-monitor`: Basic AgentMail monitoring implementation
- `agentmail-monitor-enhanced`: Enhanced monitoring with YouTube URL extraction

## Example
After applying this skill, your directory structure will look like:
```
\opt/data/
├── agentmail/
│   ├── clg_youtube_link_seen_ids.txt
│   └── clg_youtube_link_seen_urls.txt
└── scripts/
    └── agentmail/
        └── monitor_youtube.py  # Updated to reference the prefixed files
```