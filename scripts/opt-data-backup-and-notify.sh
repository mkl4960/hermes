#!/bin/bash
# Run backup at 4:00 AM Eastern Time, handles DST, then notify about changes

# Function to get next 04:00:00 in America/New_York epoch time
get_next_04_et_epoch() {
    # Get today's date in ET
    et_date=$(TZ=America/New_York date +%Y-%m-%d)
    # Try to get today 04:00:00 ET epoch
    today_04=$(TZ=America/New_YORK date -d "${et_date} 04:00:00" +%s 2>/dev/null)
    if [ $? -ne 0 ]; then
        # Try alternative date format
        today_04=$(TZ=America/New_York date +%s -d "${et_date} 04:00:00" 2>/dev/null)
    fi

    if [ -z "$today_04" ]; then
        echo "Error: Could not parse date for today 04:00:00 ET" >&2
        return 1
    fi

    now=$(date +%s)

    if [ "$today_04" -gt "$now" ]; then
        # Today's 04:00:00 ET is in the future
        echo "$today_04"
    else
        # Today's 04:00:00 ET has passed, get tomorrow's
        tomorrow_04=$(TZ=America/New_York date -d "${et_date} +1 day 04:00:00" +%s 2>/dev/null)
        if [ $? -ne 0 ]; then
            tomorrow_04=$(TZ=America/New_York date +%s -d "${et_date} +1 day 04:00:00" 2>/dev/null)
        fi
        if [ -z "$tomorrow_04" ]; then
            echo "Error: Could not parse date for tomorrow 04:00:00 ET" >&2
            return 1
        fi
        echo "$tomorrow_04"
    fi
}

# Get target epoch time for next 04:00:00 ET
target_epoch=$(get_next_04_et_epoch)
if [ $? -ne 0 ]; then
    exit 1
fi

now=$(date +%s)
sleep_seconds=$(( target_epoch - now ))

# If sleep_seconds is negative, something went wrong (shouldn't happen with our logic)
if [ $sleep_seconds -lt 0 ]; then
    echo "Warning: Calculated negative sleep time ($sleep_seconds seconds). Running backup now." >&2
    sleep_seconds=0
fi

# Sleep until target time (if needed)
if [ $sleep_seconds -gt 0 ]; then
    # Optional: log for debugging
    # echo "Sleeping for $sleep_seconds seconds until $(date -d @$target_epoch -u) UTC / $(TZ=America/New_York date -d @$target_epoch)"
    sleep $sleep_seconds
fi

# Run the actual backup script and capture output
cd /opt/data
BACKUP_OUTPUT=$(./scripts/opt-data-git-backup.sh 2>&1)
BACKUP_EXIT=$?

# Determine if there were changes based on backup script output
if echo "$BACKUP_OUTPUT" | grep -q "Committed changes"; then
    # Get the list of changed files in the last commit
    CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || echo "Unable to get changed files")
    # If git diff fails (e.g., first commit), try to list all files
    if [ "$CHANGED_FILES" = "Unable to get changed files" ]; then
        CHANGED_FILES=$(git ls-tree -r HEAD --name-only 2>/dev/null || echo "Unable to list files")
    fi
    # Format the message
    MESSAGE="🟢 Daily backup completed at 4:00 AM ET\nChanges detected:\n$CHANGED_FILES"
else
    MESSAGE="⚪ Daily backup completed at 4:00 AM ET\nNo changes detected."
fi

# Output the message (this will be captured by the cronjob tool and delivered)
echo "$MESSAGE"

exit $BACKUP_EXIT