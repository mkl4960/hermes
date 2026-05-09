#!/bin/bash
set -x

# Function to get next 04:00:00 in America/New_York epoch time
get_next_04_et_epoch() {
    echo "In function: calculating next 04:00:00 ET"
    # Get today's date in ET
    et_date=$(TZ=America/New_York date +%Y-%m-%d)
    echo "et_date: $et_date"
    # Try to get today 04:00:00 ET epoch
    today_04=$(TZ=America/New_York date -d "${et_date} 04:00:00" +%s 2>/dev/null)
    echo "today_04 (first attempt): $today_04"
    if [ $? -ne 0 ]; then
        echo "First date attempt failed, trying alternative"
        # Try alternative date format
        today_04=$(TZ=America/New_York date +%s -d "${et_date} 04:00:00" 2>/dev/null)
        echo "today_04 (second attempt): $today_04"
    fi
    
    if [ -z "$today_04" ]; then
        echo "Error: Could not parse date for today 04:00:00 ET" >&2
        return 1
    fi
    
    now=$(date +%s)
    echo "now: $now"
    echo "today_04: $today_04"
    
    if [ "$today_04" -gt "$now" ]; then
        # Today's 04:00:00 ET is in the future
        echo "Today's 04:00 is in the future"
        echo "$today_04"
    else
        # Today's 04:00:00 ET has passed, get tomorrow's
        echo "Today's 04:00 has passed, calculating tomorrow's"
        tomorrow_04=$(TZ=America/New_York date -d "${et_date} +1 day 04:00:00" +%s 2>/dev/null)
        echo "tomorrow_04 (first attempt): $tomorrow_04"
        if [ $? -ne 0 ]; then
            echo "First tomorrow attempt failed, trying alternative"
            tomorrow_04=$(TZ=America/New_York date +%s -d "${et_date} +1 day 04:00:00" 2>/dev/null)
            echo "tomorrow_04 (second attempt): $tomorrow_04"
        fi
        if [ -z "$tomorrow_04" ]; then
            echo "Error: Could not parse date for tomorrow 04:00:00 ET" >&2
            return 1
        fi
        echo "$tomorrow_04"
    fi
}

echo "Starting debug..."
target_epoch=$(get_next_04_et_epoch)
echo "Function returned: $target_epoch"
if [ $? -ne 0 ]; then
    echo "Function failed"
    exit 1
fi

now=$(date +%s)
echo "now: $now"
echo "target_epoch: $target_epoch"
sleep_seconds=$(( target_epoch - now ))
echo "sleep_seconds: $sleep_seconds"
