---
name: agentmail-integrations
description: Comprehensive guide to AgentMail integrations including sending, monitoring, persistence, and workflow automation
category: email
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [email, agentmail, integration, monitoring, automation]
    related_skills: [web-search, systematic-debugging]
---

# AgentMail Integrations

Complete guide to setting up, configuring, and using AgentMail for email sending, monitoring, and workflow automation in Hermes environments.

## Overview

This skill consolidates various AgentMail-related functionalities into a comprehensive framework covering:
- Sending emails via AgentMail API
- Setting up persistent storage for scripts and state
- Monitoring inboxes for specific criteria
- Extracting YouTube URLs and other content
- Creating automated workflows (e.g., Discord notifications)
- Managing persistent state and file organization

## When to Use

Use this skill when you need to:
- Send transactional or marketing emails via AgentMail
- Set up automated email monitoring workflows
- Integrate AgentMail with other services (Discord, etc.)
- Ensure AgentMail integrations survive container reloads
- Extract specific content from emails (YouTube URLs, etc.)
- Create deduplicated notification systems

## Core Components

### 1. Sending Emails (`agentmail` subsection)
Core functionality for sending emails using the AgentMail Python SDK.

### 2. Persistent Storage Setup (`agentmail-persistent-setup` subsection)
Guidelines for storing scripts, configurations, and state persistently to survive container reloads.

### 3. Inbox Monitoring (`agentmail-monitor` subsection)
Basic monitoring of AgentMail inboxes for specific email criteria with persistent tracking.

### 4. Enhanced Monitoring (`agentmail-monitor-enhanced` subsection)
Advanced monitoring with YouTube URL extraction, message labeling, and deduplication.

### 5. Workflow Automation (`agentmail-discord-workflow` subsection)
Complete workflows for integrating AgentMail with external services like Discord.

### 6. File Management (`agentmail-clg-youtube-link-setup` subsection)
Procedures for renaming and organizing persistent storage files.

## Quick Reference\n\n| Component | Purpose | Key Files/Directories |\n|-----------|---------|----------------------|\n| **Sending** | Send emails via AgentMail API | `agentmail` skill |\n| **Persistence** | Survive container reloads | `/opt/data/scripts/agentmail/`, `/opt/data/agentmail/` |\n| **Monitoring** | Watch for specific emails | `/opt/data/agentmail/seen_ids.txt` |\n| **Enhanced Monitoring** | Extract URLs, label messages | `/opt/data/agentmail/seen_ids.txt`, labeling |\n| **Discord Workflow** | YouTube URLs to Discord | State file, webhook URL |\n| **File Management** | Organize persistent files | Renaming procedures, prefix conventions |\n| **Monitor Locations** | Script storage guidelines | `references/monitor_locations.md` |

## Environment Setup

Before using any AgentMail functionality, ensure:
1. AgentMail Python SDK is installed
2. Valid AgentMail API key is configured
3. Persistent storage directories exist
4. Cron jobs reference persistent paths

## Common Patterns

### Basic Email Sending
```python
from agentmail import AgentMail
client = AgentMail()
inbox_id = client.inboxes.list().inboxes[0].inbox_id
response = client.inboxes.messages.send(
    inbox_id=inbox_id,
    to=["recipient@example.com"],
    subject="Test",
    text="Hello from AgentMail!"
)
```

### Persistent Monitoring Script Location
Always store monitoring scripts in: `/opt/data/scripts/agentmail/` (or in the skill's own `scripts/` directory for skill-specific monitors).

### State Tracking Files
Store seen message IDs in: `/opt/data/agentmail/seen_ids.txt`

## Verification

After setting up any AgentMail integration:
1. Test scripts manually before automating with cron
2. Verify persistent storage works across container reloads
3. Check that cron jobs reference `/opt/data/` paths
4. Validate that state files are being updated correctly
5. Monitor logs for silent operation (no output = working correctly when no new matches)
6. **Important**: Silence does NOT mean broken - the agentmail-monitor skill is designed to operate silently when no new matching emails are found. This is expected behavior, not an error.

## Troubleshooting "Broken" Monitoring

If you think your AgentMail monitoring is broken because you're not seeing output:

### Common Misinterpretations
- **Silence = Working**: The monitor script produces output ONLY when new matching emails are found. No output means it's working correctly but found nothing new.
- **Check Logs First**: Always check `/opt/data/agentmail/monitor.log` to verify the script is running and processing emails.
- **Verify Timing**: Ensure your expectations match the cron schedule (e.g., every 10 minutes for `*/10 * * * *`).

### Verification Steps
1. **Check Script Execution**: Look at the monitor.log for recent timestamps
2. **Confirm Connection**: Verify the script can connect to AgentMail and list inboxes
3. **Test Search Criteria**: Temporarily broaden search terms to see if emails exist but aren't matching
4. **Manual Test**: Run the script manually: `cd /opt/data/skills/email/agentmail-monitor && python3 scripts/monitor.py`
5. **Check Email Source**: Verify emails are actually being sent to the target inbox (`laumiex@agentmail.to`)

### Expected Log Patterns
**Healthy Silent Operation**:
```
[TIMESTAMP] Loaded X seen IDs, Y seen URLs
[TIMESTAMP] API key found (length Z)
[TIMESTAMP] AgentMail client initialized
[TIMESTAMP] Successfully listed inboxes
[TIMESTAMP] Target inbox ID: laumiex@agentmail.to
[TIMESTAMP] Fetched 50 messages
[TIMESTAMP] Total new matches: 0
[TIMESTAMP] No new matching emails - exiting
```

**When New Matches Found**:
```
[TIMESTAMP] New match found: ID=<...>, Subject=...
[TIMESTAMP] Total new matches: N
[TIMESTAMP] Updated seen IDs, now X+M seen
[TIMESTAMP] Processing message ID=<...>, body length=L
[TIMESTAMP] Extracted URLs: [...]
[TIMESTAMP] New YouTube URLs to send: [...]
[TIMESTAMP] Updated seen URLs, now Y+N seen
```

## Maintenance

- Keep AgentMail SDK updated: `uv pip install --upgrade agentmail`
- Periodically prune seen files if they grow too large
- Test after container updates to ensure persistence
- Rotate API keys periodically for security
- Monitor AgentMail dashboard for usage and billing

## Related Skills

- `web-search`: For researching AgentMail API updates or troubleshooting
- `systematic-debugging`: For diagnosing integration issues
- `devops/uv-package-installation`: For installing AgentMail SDK persistently
- `cronjob-change-notification`: For enhancing cron jobs to send notifications about changes (useful for turning silent monitors into alerting systems)

---

## Subsections

The following sections detail specific aspects of AgentMail integrations that were previously separate skills:

### Sending Emails
See the original `agentmail` skill for complete details on sending emails via AgentMail API, including HTML content, attachments, templates, and advanced features.

### Persistent Storage Setup
See the original `agentmail-persistent-setup` skill for guidelines on storing scripts, configurations, and state persistently in `/opt/data/` to survive container reloads.

### Basic Inbox Monitoring
See the original `agentmail-monitor` skill for monitoring AgentMail inboxes for specific email criteria with persistent tracking of seen messages.

### Enhanced Monitoring with URL Extraction
See the original `agentmail-monitor-enhanced` skill for advanced monitoring that extracts YouTube URLs, marks messages as read, and handles complex regex patterns.

### Discord Notification Workflow
See the original `agentmail-discord-workflow` skill for a complete workflow that monitors for YouTube live URLs, deduplicates notifications, and posts to Discord channels.

### Persistent File Management Procedures
See the original `agentmail-clg-youtube-link-setup` skill for procedures to rename AgentMail persistent storage files with custom prefixes while maintaining directory structure.

---
*This skill consolidates multiple AgentMail-related skills into a comprehensive framework for easier discovery and maintenance.*