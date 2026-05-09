---
name: cronjob-change-notification
description: Enhance existing cron jobs to send notifications about changes (e.g., git diffs) while preserving complex timing logic
category: devops
version: 1.0
---
# Enhance Cron Job with Change Detection and Notifications

## Description
This skill shows how to enhance an existing cron job (particularly one with complex timing logic like specific time-of-day execution with DST adjustment) to:
1. Preserve the existing timing/execution logic
2. Detect changes (specifically git repository changes)
3. Send formatted notifications to Discord, Slack, or other platforms
4. Handle common pitfalls like permissions and testing

## When to Use
- You have an existing cron job with non-trivial scheduling (e.g., runs at a specific local time with DST adjustment)
- You want to be notified when the job detects changes
- You want to know what specifically changed (e.g., which files were modified)
- You want to preserve the existing job's complex timing logic rather than recreate it

## Prerequisites
- Existing cron job with working timing logic
- Access to modify cron jobs via Hermes cronjob tool
- Git repository being backed up or monitored
- Notification platform access (Discord webhook, Slack webhook, etc.)
- Basic bash scripting knowledge

## Steps

### 1. Analyze the Existing Cron Job
First, understand what the existing job does and when it runs:

```bash
# List cron jobs to find the target job
cronjob list

# Examine the job details - look for:
# - Complex timing logic (might be in a wrapper script)
# - What script it actually executes
# - Where persistent data is stored
```

### 2. Preserve Existing Timing Logic
If the job uses a wrapper script for complex timing (like 4:00 AM ET with DST adjustment), **do not modify or replace it**. Instead:
- Identify the wrapper script (often has logic to sleep until target time)
- Identify the actual work script it calls
- Plan to enhance the notification *after* the timing logic but *before* or *after* the work script

### 3. Create Enhancement Script
Create a new script that:
1. Preserves any pre-work timing/logic
2. Runs the existing work script
3. Captures output and detects changes
4. Formats and sends notifications

Example structure:
```bash
#!/bin/bash
# Wrapper that preserves timing logic + adds notifications

# [OPTIONAL: If timing logic is simple, include it here]
# [BETTER: Call existing timing/wrapper script if it exists]

# Run the actual work and capture results
WORK_OUTPUT=$(cd /path/to/work && ./actual-work-script.sh 2>&1)
WORK_EXIT=$?

# Process output to detect changes
if echo "$WORK_OUTPUT" | grep -q "pattern_indicating_changes"; then
    # Extract details about what changed
    CHANGED_ITEMS=$(extract_changes_logic)
    # Format notification
    MESSAGE="✅ Job completed with changes:\n$CHANGED_ITEMS"
else
    MESSAGE="⚪ Job completed - no changes detected"
fi

# Send notification (example for Discord)
# curl -X POST -H "Content-Type: application/json" \
#   -d '{"content":"'"$MESSAGE"'"}' \
#   $DISCORD_WEBHOOK_URL

# Or for Hermes-native delivery, just output to stdout
echo "$MESSAGE"

exit $WORK_EXIT
```

### 4. For Git-Specific Change Detection
If monitoring a git repository:
```bash
# After running git operations:
if ! git diff-index --quiet HEAD --; then
    # Changes exist
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || \
                   git ls-tree -r HEAD --name-only 2>/dev/null || \
                   echo "Unable to get file list")
    
    MESSAGE="🟢 Changes detected in $(echo "$CHANGED_FILES" | wc -l) files:\n$CHANGED_FILES"
else
    MESSAGE="⚪ No changes detected"
fi
```

### 5. Update the Cron Job
Replace the existing job's prompt with your enhancement script:
```bash
cronjob update \
  --job_id <existing_job_id> \
  --prompt "Run the enhancement script: /path/to/enhancement-script.sh" \
  --deliver discord:<channel_id>  # or origin for chat, etc.
```

### 6. Set Proper Permissions
```bash
chmod +x /path/to/enhancement-script.sh
```

### 7. Test Thoroughly
```bash
# Test the enhancement script directly
/path/to/enhancement-script.sh

# Check that it:
# - Executes successfully
# - Produces expected output format
# - Handles both changes and no-changes cases
# - Has correct exit codes

# Optionally test with forced changes to verify detection works
```

## Common Patterns Preserved

### Complex Timing with DST Adjustment
Many jobs use wrapper scripts like:
```bash
# Pseudo-code for 4:00 AM ET wrapper:
export TZ=America/New_York
# Sleep until exactly 04:00:00 ET
sleep_until_4am_et
# Then call actual work script
/path/to/real-work.sh
```

**Do NOT recreate this logic** - instead, identify and preserve it by:
- Calling the existing wrapper script, OR
- Extracting and reusing the timing logic in your enhancement

### SSH Agent Management
Jobs that interact with remote repositories often need:
```bash
eval "$(ssh-agent -s)"
ssh-add "$SSH_KEY"
export GIT_SSH_COMMAND="ssh -o KnownHostsFile=$KNOWN_HOSTS"
# ... do git work ...
ssh-agent -k
```
Your enhancement script should preserve this pattern if the underlying work script relies on it.

## Platform-Specific Notification Examples

### Discord (via webhook)
```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
curl -X POST -H "Content-Type: application/json" \
  -d "{\"content\":\"$MESSAGE\"}" \
  "$DISCORD_WEBHOOK_URL"
```

### Slack (via webhook)
```bash
SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"$MESSAGE\"}" \
  "$SLACK_WEBHOOK_URL"
```

### Hermes Native Delivery
Simply output to stdout - the cronjob tool will capture and deliver it:
```bash
echo "$MESSAGE"
# No additional curl needed when using --deliver parameter
```

## Verification Steps
After updating the cron job:
1. Check the job listing: `cronjob list`
2. Verify next run time is scheduled
3. Manually run the enhancement script to test
4. Check that notifications arrive correctly formatted
5. Verify the underlying work still completes successfully

## Troubleshooting

### "Permission denied" Errors
- Fix: `chmod +x /path/to/script.sh`
- Verify execute permissions on all scripts in the chain

### No Notifications Received
- Check script output with manual run
- Verify cron job deliver target is correct
- Check platform webhook URLs and permissions
- For Hermes delivery, check if job is delivering to correct chat/channel

### Timing Issues
- If job runs at wrong time, you may have accidentally replaced timing logic
- Verify you're preserving existing wrapper/scripts
- Check timezone settings in timing logic

### Change Detection Not Working
- Verify git repository is in expected state
- Check that you're looking for changes in the right commit range
- Ensure working directory is correct when running git commands

## Environment-Specific Tips

### Hermes Container Environment
- Store scripts in `/opt/data/scripts/` for persistence
- SSH keys for git operations should be in `/opt/data/home/.ssh/`
- The `/opt/data/` directory survives container reloads
- Test scripts manually before relying on cron execution

### Preserving Existing Skills
If the existing job uses a skill (like agentmail-monitor):
- Look at the skill to understand what it does
- Your enhancement should wrap/pre/post the skill's core functionality
- Consider if you need to modify the skill itself vs. wrapping it

## Related Skills
- `git-backup-cronjob`: For setting up new git backup cron jobs from scratch
- `fix-agentmail-cronjob-path`: For fixing specific cron job path issues
- `hermes-persistent-storage`: For managing files that survive container reloads
- `uv-package-installation`: For installing packages in restricted environments

## Example: Enhancing opt-data-daily-backjob
This skill was created based on enhancing the Hermes opt-data-daily-backup job:
1. Preserved the 4:00 AM ET with DST adjustment timing logic
2. Added git change detection after backup completion
3. Formatted Discord notifications with emojis and file lists
4. Updated the existing cron job to use the enhancement script
5. Maintained all existing functionality while adding notifications