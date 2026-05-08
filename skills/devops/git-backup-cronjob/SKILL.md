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

### 2. Set Up .gitignore (Optional but Recommended)
Create or update `.gitignore` to exclude sensitive files:
```bash
# Example: exclude .env file
echo ".env" >> .gitignore
# Or if file exists, ensure the line is present
if ! grep -q "^\.env$" .gitignore; then
  echo ".env" >> .gitignore
fi
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