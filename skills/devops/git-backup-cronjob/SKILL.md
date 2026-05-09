---
name: git-backup-cronjob
description: Automatically backup a directory to a GitHub repository using SSH authentication and a cron job
category: devops
version: 1.0
---
# Git Backup Cronjob Skill

## Description
Automatically backup a directory to a GitHub repository using SSH authentication and a cron job. This skill handles git repository setup, SSH key generation, backup script creation, and cron scheduling.

## When to Use
- You want to regularly backup a directory (e.g., configuration files) to a remote GitHub repository
- You need automated, versioned backups without manual intervention
- You prefer SSH authentication over HTTPS for reliability in automated environments

## Prerequisites
- Access to a GitHub account where you can add SSH keys
- The target directory you wish to backup
- Cron available in the environment
- Understanding of what files should be backed up (avoid secrets, logs, etc.)

## Steps

### 1. Prepare the Target Directory
```bash
# Navigate to the directory you want to backup
cd /path/to/your/directory

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
  git init
  git config user.name "Hermes Bot"  # Optional: set your preferred name
  git config user.email "hermes@example.com"  # Optional: set your preferred email
fi

# Add GitHub remote (replace with your repository URL)
git remote add origin git@github.com:username/repository.git
# Verify remote
git remote -v
```

### 2. Set Up Comprehensive .gitignore (Critical for Security)
Create or update `.gitignore` to exclude sensitive files and directories:

```bash
# Hermes-specific exclusions
# SSH keys and authentication
echo '/.ssh/' >> .gitignore
echo '/home/.ssh/' >> .gitignore

# Environment files and secrets
echo '.env' >> .gitignore
echo '*.env' >> .gitignore
echo 'auth.json' >> .gitignore
echo 'secrets.json' >> .gitignore

# Databases and model caches
echo 'state.db' >> .gitignore
echo 'response_store.db' >> .gitignore
echo '*.sqlite' >> .gitignore
echo 'model_cache/' >> .gitignore

# Logs and temporary files
echo 'logs/' >> .gitignore
echo 'sessions/' >> .gitignore
echo 'cache/' >> .gitignore
echo '.heroku/' >> .gitignore

# Hermes-specific directories that contain ephemeral or sensitive data
echo 'memories/' >> .gitignore
echo '.skills_prompt_snapshot.json' >> .gitignore

# Binaries and platform-specific files (optional, based on your needs)
echo 'bin/' >> .gitignore

# After adding, verify important files are NOT excluded
# You can test with: git check-ignore -v <file>
```

### 3. Generate SSH Key for Authentication (if not already present)
```bash
# Create ~/.ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Generate Ed25519 key pair (replace email with your identifier)
ssh-keygen -t ed25519 -f ~/.ssh/hermes_github -N "" -C "hermes@your-host"

# Add the public key to your GitHub account:
#   cat ~/.ssh/hermes_github.pub
# Copy the output and add it at: GitHub → Settings → SSH and GPG keys → New SSH key

# Add GitHub to known_hosts to prevent interactive prompts
ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null
chmod 600 ~/.ssh/known_hosts

# In Hermes/container environments, also ensure known_hosts is accessible:
mkdir -p /opt/data/.ssh
cp ~/.ssh/known_hosts /opt/data/.ssh/known_hosts
chmod 600 /opt/data/.ssh/known_hosts
```

### 4. Create the Backup Script
Save this as `/opt/data/scripts/git-backup.sh` (or your preferred location):
```bash
#!/bin/bash
set -e

# ===== CONFIGURATION =====
TARGET_DIR="/path/to/your/directory"  # <-- CHANGE THIS
SSH_KEY="$HOME/.ssh/hermes_github"    # <-- ADJUST IF YOU USED A DIFFERENT PATH
REPO_ORIGIN="origin"                  # Usually 'origin' unless you changed it
BRANCH="master"                       # Or 'main' depending on your repo default
# =========================

# Start ssh-agent and add the key
eval "$(ssh-agent -s)"
trap 'ssh-agent -k' EXIT  # Ensure agent is killed when script exits

ssh-add "$SSH_KEY"

# Change to target directory
cd "$TARGET_DIR"

# Add all changes
git add .

# Commit if there are changes
if ! git diff-index --quiet HEAD --; then
  TIMESTAMP=$(date +'%Y-%m-%d %H:%M:%S')
  git commit -m "Automated backup: $TIMESTAMP"
  echo "[$(date)] Committed changes"
else
  echo "[$(date)] No changes to commit"
fi

# Push to remote
git push "$REPO_ORIGIN" "$BRANCH"
```

Make the script executable:
```bash
chmod +x /opt/data/scripts/git-backup.sh
```

### 5. Set Up the Cron Job
To run the backup daily at 4 AM:
```bash
# Using the Hermes cronjob tool (preferred method):
# cronjob create --name "git-backup-daily" --schedule "0 4 * * *" \
#   --prompt "Run the git backup script" \
#   --deliver origin

# Or manually via crontab -e:
# 0 4 * * * /opt/data/scripts/git-backup.sh >> /var/log/git-backup.log 2>&1
```

## Troubleshooting

### SSH Connection Issues
- Verify the SSH key is added to the ssh-agent: `ssh-add -l`
- Test the connection: `ssh -T git@github.com`
- Ensure the public key is correctly added to your GitHub account

### Permission Denied (publickey)
- Check that the SSH key file has correct permissions: `chmod 600 ~/.ssh/hermes_github`
- Verify you're using the correct key in the script and ssh-agent

### No Changes to Commit
- This is normal if the directory hasn't changed
- Check that your .gitignore is working correctly if you expect certain files to be ignored

### Repository Detached Head
- Ensure you're on the correct branch before pushing
- The script assumes you're pushing to the default branch (master/main)

### Host Key Verification Failed
- In some environments (like Hermes), SSH may look for known_hosts in unexpected locations
- Solution: Ensure known_hosts file exists in all possible locations SSH might check:
  ```bash
  # Common locations:
  mkdir -p ~/.ssh
  ssh-keyscan github.com >> ~/.ssh/known_hosts
  
  # For Hermes-like environments:
  mkdir -p /opt/data/.ssh
  cp ~/.ssh/known_hosts /opt/data/.ssh/known_hosts
  chmod 600 ~/.ssh/known_hosts /opt/data/.ssh/known_hosts
  ```
- Alternatively, set GIT_SSH_COMMAND environment variable to specify known_hosts location:
  ```bash
  export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=/path/to/known_hosts"
  ```

### Could not read Username for 'https://github.com'
- This indicates the remote is set up for HTTPS instead of SSH
- Solution: Switch remote to use SSH:
  ```bash
  git remote set-url origin git@github.com:username/repository.git
  ```
- Verify with: `git remote -v` (should show git@github.com:... URLs)

## Customization

### Different Schedule
- Adjust the cron schedule: `0 4 * * *` (daily at 4 AM)
- Examples: `0 */6 * * *` (every 6 hours), `30 2 * * 0` (weekly on Sunday at 2:30 AM)

### Automatic DST Adjustment for Time Zone-Specific Times
To run a job at a specific local time (like 4am Eastern Time) that automatically adjusts for Daylight Saving Time, there are two common approaches:

#### Approach 1: Frequent Checking (Simple but less efficient)
1. Create a wrapper script that:
   - Sets the desired timezone (e.g., `export TZ=America/New_York`)
   - Checks if current time matches the target time (e.g., exactly 4:00:00 AM)
   - Runs the backup only when conditions are met

2. Schedule the wrapper to run frequently (e.g., every minute) using cron:
   ```bash
   # Runs the wrapper every minute
   * * * * * /path/to/wrapper-script.sh
   ```

Example wrapper script for 4am Eastern Time backup:
```bash
#!/bin/bash
# Set timezone to Eastern Time
export TZ=America/New_York

# Get current hour and minute
HOUR=$(date +%H)
MINUTE=$(date +%M)

# Check if it's exactly 4:00 AM
if [[ "$HOUR" == "04" && "$MINUTE" == "00" ]]; then
    echo "$(date): Running Eastern Time backup..."
    /path/to/your/backup-script.sh
fi
```

#### Approach 2: Sleep Until Target Time (Recommended - More efficient)
1. Create a wrapper script that calculates the exact next occurrence of the target time and sleeps until then:

```bash
#!/bin/bash
# Set timezone to Eastern Time
export TZ=America/New_York

# Function to calculate seconds until next 04:00:00
get_sleep_seconds() {
    # Get current time in seconds since epoch
    now=$(date +%s)
    # Get today's 04:00:00 in seconds since epoch
    today_4am=$(date -d "today 04:00:00" +%s)
    
    # If it's already past 04:00:00 today, target tomorrow
    if [ "$now" -gt "$today_4am" ]; then
        target=$(date -d "tomorrow 04:00:00" +%s)
    else
        target=$today_4am
    fi
    
    # Calculate seconds to sleep
    echo $((target - now))
}

# Sleep until the target time
sleep_seconds=$(get_sleep_seconds)
echo "$(date): Sleeping for $sleep_seconds seconds until 04:00:00 Eastern Time"
sleep "$sleep_seconds"

echo "$(date): Running Eastern Time backup..."
/path/to/your/backup-script.sh
```

2. Schedule the wrapper to run once daily (e.g., at midnight UTC) using cron:
   ```bash
   # Runs the wrapper daily at midnight UTC
   0 0 * * * /path/to/wrapper-script.sh
   ```

This approach is more efficient as it only wakes up once per day at the exact target time, rather than running a check every minute. It was implemented for the Hermes `/opt/data` backup to GitHub at 4am Eastern Time.

### Multiple Directories
- Create separate scripts for each directory, or modify the script to accept directory as argument
- Or create multiple cron jobs with different scripts

### Different Repository Hosting
- For GitLab, Bitbucket, etc., change the remote URL and known_hosts line
- Example for GitLab: `ssh-keyscan gitlab.com >> ~/.ssh/known_hosts`

## Security Notes
- The SSH key should have no passphrase for fully automated backups (as shown)
- Consider using deploy keys with write access limited to the specific repository
- Regularly rotate SSH keys and remove old ones from GitHub
- Ensure backup directory is properly secured

## Verification
- Check cron job status: `cronjob list`
- View logs (if using Hermes cronjob): Check the delivery destination
- Verify backups in GitHub: Check commit history

## Related Skills
- `hermes-persistent-storage`: For managing files that survive container reloads
- `uv-package-installation`: For installing packages in restricted environments

## Environment-Specific Tips

### Hermes Container Environment
- Persistent data should be stored in `/opt/data/` (not ~/.hermes)
- SSH keys for cron jobs should be placed in `/opt/data/home/.ssh/` for persistence
- The `/opt/data/` directory is designed to survive container reloads
- When backing up Hermes configurations, target `/opt/data/` rather than ~/.hermes
- Always test scripts manually before scheduling via cronjob

### Hermes-Specific DST-Adjusting Backup Implementation
For the Hermes environment, we implemented a specific solution for backing up `/opt/data` to GitHub at 4am Eastern Time with automatic DST adjustment:

1. **Wrapper Script Location**: `/opt/data/scripts/opt-data-backup-wrapper.sh`
2. **Cron Schedule**: `* * * * *` (runs every minute)
3. **Timezone Handling**: Uses `export TZ=America/New_York` to get Eastern Time
4. **Precision Check**: Only runs when time is exactly 04:00 (HH:MM)
5. **Backup Script**: Calls `/opt/data/scripts/opt-data-git-backup.sh` which performs the actual git operations

This approach eliminates the need to manually adjust cron schedules twice yearly for DST changes while maintaining secure backups that exclude sensitive data via a comprehensive .gitignore.

### Working with Existing Configurations
- Before creating new cronjobs, check existing ones with `cronjob list`
- It's often more efficient to fix existing misconfigured jobs than create duplicates
- When fixing cronjobs, ensure you understand what skills the original job required