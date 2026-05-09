#!/bin/bash
# Debug: compute sleep time to next 04:00:00 America/New_York

get_next_04_et_epoch() {
    et_date=$(TZ=America/New_York date +%Y-%m-%d)
    today_04=$(TZ=America/New_York date -d "${et_date} 04:00:00" +%s 2>/dev/null)
    if [ $? -ne 0 ]; then
        today_04=$(TZ=America/New_York date +%s -d "${et_date} 04:00:00" 2>/dev/null)
    fi
    if [ -z "$today_04" ]; then
        echo "Error: Could not parse date for today 04:00:00 ET" >&2
        return 1
    fi
    now=$(date +%s)
    if [ "$today_04" -gt "$now" ]; then
        echo "$today_04"
    else
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

target_epoch=$(get_next_04_et_epoch)
if [ $? -ne 0 ]; then
    exit 1
fi
now=$(date +%s)
sleep_seconds=$(( target_epoch - now ))
echo "Sleep seconds: $sleep_seconds"
if [ $sleep_seconds -gt 0 ]; then
    echo "Will sleep for $sleep_seconds seconds ($((sleep_seconds/3600)) hours)"
    date -u
    echo "Wake up at UTC: $(date -u -d @$target_epoch)"
    TZ=America/New_York date
    echo "Wake up at ET: $(TZ=America/New_York date -d @$target_epoch)"
else
    echo "Sleep seconds <= 0, would run now"
fi
