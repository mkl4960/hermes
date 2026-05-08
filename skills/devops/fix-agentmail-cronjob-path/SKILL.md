---
name: fix-agentmail-cronjob-path
category: devops
description: Fix AgentMail cronjob path to use skill-based monitoring script.
---

# Fix AgentMail Cronjob Path

## Problem
Cronjob was trying to run non-existent script at `/opt/data/scripts/check_agentmail.py` causing "No such file or directory" error.

## Solution
Updated cronjob to use the proper skill-based AgentMail monitoring script.

## Steps
1. Identify the correct monitoring script location:
   - Skill: `agentmail-monitor`
   - Script: `/opt/data/skills/email/agentmail-monitor/scripts/agentmail/monitor.py`

2. Update the cronjob with the correct command:
   ```bash
   /opt/hermes/.venv/bin/python /opt/data/skills/email/agentmail-monitor/scripts/agentmail/monitor.py
   ```

3. Verify the script works:
   - Runs successfully (exit code 0)
   - Uses persistent storage in `/opt/data/agentmail/` for tracking
   - Only outputs when new matching emails are found (silent cron operation)

## Important Notes
- The AgentMail monitor script is designed for silent cron operation
- It only produces output when it finds NEW unseen emails matching criteria
- Matching emails that have already been processed are skipped (no output)
- Tracking files:
  - Seen message IDs: `/opt/data/agentmail/seen_ids.txt`
  - Seen YouTube URLs: `/opt/data/agentmail/seen_urls.txt`
- Cron schedule: Every 10 minutes (`*/10 * * * *`)
- Delivery: Returns output to the originating chat

## Verification
- Check cronjob status: Lists job with correct command/path
- Test manual run: `/opt/hermes/.venv/bin/python /opt/data/skills/email/agentmail-monitor/scripts/agentmail/monitor.py`
- Verify no errors and appropriate silent behavior when no new matches