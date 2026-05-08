---
name: agentmail-discord-workflow
description: Workflow for monitoring AgentMail inbox for YouTube live URLs, deduplicating notifications, and posting to Discord channel.
category: email
version: 1.0
---

# AgentMail to Discord Notification Workflow

## Purpose
This workflow describes how to monitor an AgentMail inbox for new emails containing YouTube live URLs, deduplicate against previously processed notifications, and post new URLs to a specified Discord channel (not DM).

## When to Use
- You receive emails via AgentMail that contain YouTube live stream links.
- You want to avoid spamming duplicate notifications for the same live streams.
- You want to consolidate notifications in a Discord channel for team visibility.

## Prerequisites
- AgentMail Python SDK installed and configured (refer to `agentmail` skill).
- Access to AgentMail API key stored securely (environment variable recommended).
- Discord webhook URL for the target channel.
- Persistent storage location available (e.g., `/opt/data/` for files that survive container reloads).

## Workflow Overview

### 1. State Management
Maintain a persistent state file to track:
- Processed email IDs (to avoid re-processing same emails)
- Processed YouTube URLs (to avoid duplicate notifications)

**Recommended storage**: `/opt/data/scripts/agentmail_state.json`
```json
{
  "processed_email_ids": ["email_id_1", "email_id_2"],
  "processed_urls": ["https://youtube.com/live/abc123", "https://youtube.com/live/def456"]
}
```

### 2. Monitoring Process
Repeat these steps on a schedule (e.g., via cron every 5 minutes):

**Step A: Fetch new emails**
- Use the `agentmail` skill to list recent messages in your inbox.
- Filter for emails whose IDs are not in `processed_email_ids`.

**Step B: Extract YouTube URLs**
- From each new email body, extract URLs matching pattern: `https://youtube.com/live/[^\s]+`
- Use regex or string parsing appropriate for your language.

**Step C: Deduplicate and notify**
- For each extracted URL:
  - If URL not in `processed_urls`:
    - Add to notifications to send
    - Add URL to `processed_urls` set
- Send each new URL as a separate message to Discord webhook.
- Add processed email IDs to `processed_email_ids` set.

**Step D: Persist state**
- Write updated `processed_email_ids` and `processed_urls` lists back to state file.

### 3. Discord Notification
- Send messages to Discord via webhook POST request.
- Message format: `New YouTube live: [URL]`
- Handle rate limits by delaying between messages if needed.

## Implementation Notes

### Security
- Never hardcode API keys or webhook URLs in scripts.
- Use environment variables or secure secret management.
- The `agentmail` skill provides secure patterns for SDK usage.

### Persistence
- Store state file in `/opt/data/` directory to survive container reloads.
- Ensure the directory is writable by your script/cron job.

### Error Handling
- Implement try/catch blocks for network operations.
- Log errors appropriately for debugging.
- Consider exponential backoff for failed Discord posts.

### Customization
- Adjust YouTube URL regex if your emails use different formats.
- Modify Discord message formatting as needed.
- Change polling frequency based on email volume and latency requirements.

## Using Existing Skills
This workflow leverages:
- `agentmail` skill for secure email fetching via AgentMail SDK.
- Standard Python libraries (`os`, `json`, `re`, `requests`) for orchestration.
- Cron or scheduler for periodic execution.

## Verification Steps
1. Test state file creation and updates.
2. Verify email fetching works with `agentmail` skill.
3. Confirm URL extraction matches your email format.
4. Test Discord webhook connectivity separately.
5. Run workflow manually before automating with cron.
6. Check that duplicates are suppressed after first run.

## Maintenance
- Monitor state file size; consider pruning old entries if needed long-term.
- Update Discord webhook if regenerated; update environment variable.
- Keep AgentMail SDK updated per `agentmail` skill recommendations.

---
*Workflow documentation created by Hermes Agent based on implemented solution for deduplicated YouTube live notifications.*