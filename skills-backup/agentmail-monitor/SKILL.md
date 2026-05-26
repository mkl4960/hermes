---
name: agentmail-monitor
description: Monitor AgentMail inbox for specific emails and extract YouTube URLs
category: email
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [email, agentmail, monitoring, automation]
    related_skills: [agentmail-integrations, web-search]
---

# AgentMail Monitor Skill

This skill provides a monitoring solution for AgentMail inboxes that checks for emails matching specific criteria and extracts YouTube URLs from them. Designed for silent cron operation where it only outputs when new matches are found.

## Overview

The agentmail-monitor skill monitors an AgentMail inbox for emails containing specific phrases in the subject line, extracts YouTube URLs from the email body, and tracks processed messages to avoid duplicate notifications.

## When to Use

Use this skill when you need to:
- Monitor an AgentMail inbox for specific email patterns
- Extract URLs (particularly YouTube links) from matching emails
- Create automated notifications (e.g., to Discord) when new content arrives
- Avoid duplicate notifications through persistent tracking
- Run as a silent cron job that only outputs when there's something to report

## How It Works

1. Loads environment variables from `/opt/data/.env`
2. Initializes AgentMail client using API key from environment
3. Finds target inbox by email address (`laumiex@agentmail.to`)
4. Fetches recent messages (limit 50)
5. For each message, checks if subject contains BOTH:
   - "URL for"
   - "CLGNJ English Sunday Worship Service"
6. For matching messages not yet seen:
   - Fetches full message to get body
   - Extracts YouTube URL using regex pattern
   - Collects URLs for output
7. Marks all processed messages as seen (whether they matched or not)
8. Saves updated seen IDs to persistent storage
9. Outputs YouTube URLs (one per line) only when new matches found
10. Exits silently when no new matches (designed for cron)

## Configuration

The monitoring script (`scripts/monitor.py`) can be customized by modifying these variables at the top:

- `SEEN_FILE`: Path to persistent storage for seen message IDs (default: `/opt/data/agentmail/clg_youtube_link_seen_ids.txt`)
- `TARGET_EMAIL`: Email address to monitor (default: `laumiex@agentmail.to`)
- `SEARCH_PHRASES`: List of phrases that MUST all be in subject (default: `['URL for', 'CLGNJ English Sunday Worship Service']`)

## Files Created

- `/opt/data/agentmail/clg_youtube_link_seen_ids.txt` - Tracks seen message IDs
- `/opt/data/agentmail/monitor.log` - Activity log (if logging is enabled)

## Dependencies

- AgentMail Python SDK (`agentmail` package)
- Valid AgentMail API key in environment (`AGENTMAIL_API_KEY`)
- Access to AgentMail inbox `laumiex@agentmail.to`

## Setup

1. Ensure AgentMail SDK is installed: `uv pip install agentmail`
2. Configure `.env` file with `AGENTMAIL_API_KEY`
3. Verify inbox `laumiex@agentmail.to` exists and is accessible
4. The monitoring script will create necessary storage directories/files on first run

## Usage in Cron Jobs

This skill is designed to be used with the `cronjob` tool for scheduled monitoring:

```bash
hermes cron create "*/10 * * * *" --skills agentmail-monitor --prompt "Run agentmail monitor script" --name "agentmail-monitor" --deliver discord:1494191383219798197
```

The skill itself doesn't execute commands - it provides the monitoring script that gets run by the cron job's command:
`/usr/bin/python3 /opt/data/skills/email/agentmail-monitor/scripts/monitor.py`

## Expected Behavior

- **Silent operation**: When no new matching emails are found, the script produces NO output (this is normal and expected)
- **Active operation**: When new matching emails are found, prints YouTube URLs (one per line)
- **Persistent tracking**: Remembers which messages have been processed across runs
- **Cron-friendly**: Designed to be silent when there's nothing to report, reducing noise

## Troubleshooting

If you're not seeing expected YouTube URL notifications:

1. **Check if script is running**: Look at `/opt/data/agentmail/monitor.log` for recent activity
2. **Verify email delivery**: Confirm emails are being sent to `laumiex@agentmail.to`
3. **Check search criteria**: Ensure email subjects contain BOTH required phrases
4. **Test manually**: Run `/opt/data/skills/email/agentmail-monitor/scripts/monitor.py` directly to see output
5. **Check AgentMail connection**: Verify API key is valid and inbox is accessible
6. **Review seen files**: Check `/opt/data/agentmail/clg_youtube_link_seen_ids.txt` if you suspect tracking issues

## Example Log Output (Healthy Silent Operation)

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

## Example Log Output (When Matches Found)

```
[TIMESTAMP] New match found: ID=<...>, Subject=Fwd: URL for DATE CLGNJ English Sunday Worship Service
[TIMESTAMP] Total new matches: N
[TIMESTAMP] Updated seen IDs, now X+M seen
[TIMESTAMP] Processing message ID=<...>, body length=L
[TIMESTAMP] Extracted URLs: [...]
[TIMESTAMP] New YouTube URLs to send: [...]
[TIMESTAMP] Updated seen URLs, now Y+N seen
```

## Notes

- The skill is designed to work with the specific email pattern used for CLGNJ English Sunday Worship Service notifications
- To monitor different criteria, modify the `SEARCH_PHRASES` in the monitor.py script
- The YouTube URL extraction regex matches standard youtube.com/watch?v= and youtu.be/ formats
- For different URL patterns, adjust the `extract_youtube_url()` function in monitor.py

## 🛡️ Skill Persistence & Recovery

Occasionally, the agentmail-monitor skill file (SKILL.md) may go missing due to system/container updates, cleanup processes, or synchronization issues. This results in cron job errors like:
```
⚠️ Skill(s) not found and skipped: agentmail-monitor
```

**To recover:**
1. Verify the skill exists: `hermes skills list | grep agentmail-monitor`
2. If missing, the skill can be restored from backup or recreated
3. Ensure the monitoring script exists at `/opt/data/skills/email/agentmail-monitor/scripts/monitor.py`
4. Reattach the skill to any affected cron jobs: `hermes cron edit <job_id> --skills agentmail-monitor`

## 🔇 Expected Silent Operation

The agentmail-monitor skill is designed for **silent cron operation**:
- ✅ **NO output** when no new matching emails are found (this is normal and expected)
- ✅ **Outputs YouTube URLs** (one per line) only when new matches are detected
- 📊 Check `/opt/data/agentmail/monitor.log` to verify the script is running correctly
- 🚫 Silence does NOT indicate broken operation - it means the monitor found nothing new to report

## 💡 Pro Tip: Verifying Operation

To quickly verify the monitor is working:
```bash
# Check recent log activity
tail -20 /opt/data/agentmail/monitor.log

# Test manual execution (should show output if new matches exist)
/opt/data/skills/email/agentmail-monitor/scripts/monitor.py

# Verify cron job status
hermes cron list | grep agentmail-monitor
```