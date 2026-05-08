---
name: resolve-script-paths
category: software-development
description: Approach for locating and executing scripts when the expected path doesn't exist in Hermes environments
---

# Resolve and Execute Misplaced Scripts

## Approach for locating and executing scripts when the expected path doesn't exist in Hermes environments

Sometimes skill instructions or documentation reference scripts at specific paths that don't actually exist, either due to environment variations, outdated instructions, or alternative implementations being present. This skill provides a systematic approach to locate the correct script and execute it appropriately.

## When to Use This Skill

Use this approach when:
- You're instructed to run a script at a specific path that returns "No such file or directory"
- You need to find alternative implementations of a script or tool
- Skill instructions point to generic paths that may have environment-specific variants
- You discover multiple similar scripts and need to determine which is most appropriate for your task

## Step-by-Step Procedure

### 1. Verify the Expected Path Doesn't Exist
First, confirm that the instructed path is indeed invalid:

```bash
ls -la /path/to/instructed/script.py
# or
/test /path/to/instructed/script.py && echo "Exists" || echo "Missing"
```

### 2. Search for Similar Files
Use the find command to locate files with similar names:

```bash
# Find files matching the script name anywhere in /opt/data
find /opt/data -name "script.py" -type f 2>/dev/null

# Find files containing part of the expected path
find /opt/data -path "*agentmail*" -name "*monitor*" -type f 2>/dev/null

# Broader search if needed
find /opt/data -name "*monitor*" -type f 2>/dev/null | head -20
```

### 3. Explore Directory Structure
If search yields too many results or none, explore likely directories:

```bash
# Check common locations for scripts in Hermes
ls -la /opt/data/scripts/
ls -la /opt/data/skills/*/scripts/
ls -la /opt/data/agentmail/  # if applicable

# Look for environment-specific implementations
ls -la /opt/data/scripts/agentmail/
```

### 4. Examine Discovered Scripts
Once you find candidate scripts, examine them to determine which is most appropriate:

```bash
# Look at the script content to understand its purpose
head -30 /path/to/candidate/script.py
grep -E "SEARCH_PHRASES|YOUTUBE|extract.*url" /path/to/candidate/script.py

# Check if it matches your specific requirements
# For example, if you need YouTube URL extraction, look for regex patterns
```

### 5. Execute the Appropriate Script
Run the script you've determined is correct:

```bash
# Use the appropriate Python interpreter (often in .venv)
/opt/hermes/.venv/bin/python /path/to/correct/script.py

# Or if it's executable and has shebang:
/path/to/correct/script.py
```

### 6. Handle Output According to Expectations
Many monitoring scripts are designed for silent operation:

- If the script produces no output and exits with code 0, it likely means "no matches found" - this is normal
- Only consider it an error if the script exits with a non-zero code
- Follow any specific instructions about what constitutes valid output

## Example: AgentMail Monitor Script Resolution

This approach was successfully used when:
- Instructed to run: `/opt/data/skills/agentmail-monitor/scripts/agentmail/monitor.py`
- Actual script was found at: `/opt/data/scripts/agentmail/monitor_youtube.py`
- The YouTube-specific variant was appropriate for extracting YouTube URLs from emails
- Script executed successfully with no output (indicating no new matching emails)

## Verification Steps

After executing a located script:
1. Check exit code: `echo $?` (should be 0 for successful execution)
2. Look for any side effects: Did it create/update expected files?
   - For AgentMail monitors: check `/opt/data/agentmail/seen_ids.txt` for updates
3. If appropriate, test with known good input to verify functionality
4. Document the correct path for future reference

## Common Pitfalls and Solutions

### Pitfall: Assuming the Instructed Path is Correct
**Solution**: Always verify existence before attempting execution. Don't waste time debugging execution failures that are actually just missing files.

### Pitfall: Choosing the Wrong Variant Script
**Solution**: Examine script contents for key identifiers of functionality:
- Look for specific search phrases in the code
- Check for specialized functions (like URL extraction)
- Read comments and documentation headers
- Compare against your specific requirements

### Pitfall: Missing Environment Dependencies
**Solution**: Check if the script requires specific environment variables or virtual environments:
- Look for `load_env_file` or similar patterns in the script
- Check if it imports special modules that might need installation
- Use the same Python interpreter/path that would be used in the original context

### Pitfall: Overlooking Side Effects Like Message Labeling
**Solution**: Some scripts do more than just print output - they may:
- Mark messages as read/unread
- Apply labels
- Update tracking files
- These side effects are often important for proper operation

## Environment Notes for Hermes

In Hermes environments:
- Scripts are often found in `/opt/data/scripts/` rather than under skills
- Skills may provide templates (SKILL.md) while actual implementations live elsewhere
- The `.venv` directory at `/opt/hermes/.venv` often contains the appropriate Python interpreter
- Persistent storage for tracking is commonly under `/opt/data/`
- Environment variables may be loaded from `/opt/data/.env`

## Related Skills

- `devops/troubleshooting-file-modification`: For actually modifying files once located
- `hermes-environment/hermes-persistent-storage`: For understanding where to look for persistent data
- `email/agentmail`: For sending emails via AgentMail (complementary to monitoring)
- `software-development/systematic-debugging`: General debugging approach that this skill complements

## When Not to Use This Skill

Don't use this approach when:
- The instructed path exists and executes correctly - just run it directly
- You need to create a new script from scratch (consider saving as a skill instead)
- The task requires interactive user input (cron jobs and automated tasks should be silent)
- You're dealing with compiled binaries rather than scripts (use `which` or `find` with `-executable`)

This approach is most valuable for interpreting and adapting documentation or skill instructions to the specific Hermes environment you're working in.