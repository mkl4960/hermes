# AgentMail Monitor Script Locations

This document describes the standard locations for AgentMail monitoring scripts in Hermes environments.

## Primary Location
`/opt/data/scripts/agentmail/` - The main directory for persistent monitoring scripts that should survive container reloads.

## Skill-Specific Location
`/opt/data/skills/email/agentmail-monitor/scripts/` - Location for monitors that are part of a specific skill and should be versioned with the skill.

## Best Practices
1. Always store monitoring scripts in persistent storage (`/opt/data/`) to prevent loss on container updates.
2. For skill-integrated monitors, keep them within the skill's directory structure.
3. Ensure cron jobs reference the persistent path, not temporary or skill-source paths.
4. When copying a skill-specific monitor to persistent storage, maintain the same filename and permissions.

## Example Cron Job
```cron
# Monitor for YouTube links in AgentMail (runs every 5 minutes)
*/5 * * * * /usr/bin/python3 /opt/data/scripts/agentmail/monitor_youtube.py >> /var/log/agentmail-monitor.log 2>&1
```