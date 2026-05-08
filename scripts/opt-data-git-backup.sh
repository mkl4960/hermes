#!/bin/bash
set -e

# Path to the data directory
DATA_DIR="/opt/data"
SSH_KEY="/opt/data/home/.ssh/hermes_github"
KNOWN_HOSTS="/opt/data/home/.ssh/known_hosts"

# Start ssh-agent and add the key
eval "$(ssh-agent -s)"
ssh-add "$SSH_KEY"

# Set git to use our known hosts file
export GIT_SSH_COMMAND="ssh -o UserKnownHostsFile=$KNOWN_HOSTS"

# Change to data directory
cd "$DATA_DIR"

# Add all changes (respecting .gitignore)
git add .

# Commit if there are changes
if ! git diff-index --quiet HEAD --; then
    git commit -m "Daily backup $(date +'%Y-%m-%d %H:%M:%S')"
    echo "Committed changes"
else
    echo "No changes to commit"
fi

# Push to origin master
git push origin master

# Clean up ssh-agent
ssh-agent -k