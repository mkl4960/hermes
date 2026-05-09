#!/bin/bash
# Test version of the backup time calculator

# Function to get next 04:00:00 in America/New_York epoch time
get_next_04_et_epoch() {
    # Get today's date in ET
    et_date=$(TZ=America/New_York date +%Y-%m-%d)
    # Try to get today 04:00:00 ET epoch
    today_04=$(TZ=America/New_York date -d "${et_date} 04:00:00" +%s 2>/dev/null)
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

echo "=== Backup Time Calculator Test ==="
echo "Current UTC time: $(date -u)"
echo "Current ET time: $(TZ=America/New_York date)"
echo "Target epoch (next ET 04:00:00): $target_epoch"
echo "Target time UTC: $(date -d @$target_epoch -u)"
echo "Target time ET: $(TZ=America/New_York date -d @$target_epoch)"
echo "Now epoch: $now"
echo "Seconds to sleep: $sleep_seconds"
echo "Hours to sleep: $((sleep_seconds / 3600))"
echo "Minutes to sleep: $((sleep_seconds / 60))"
if [ $sleep_seconds -gt 0 ]; then
    echo "Will sleep for $sleep_seconds seconds"
else
    echo "Would run backup now (negative or zero sleep time)"
fi
echo "===================================="
