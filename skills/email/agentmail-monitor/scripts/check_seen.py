#!/opt/hermes/.venv/bin/python3
import os

SEEN_FILE = '/opt/data/agentmail/seen_ids.txt'
if not os.path.exists(SEEN_FILE):
    print("Seen file not found")
    exit(1)

with open(SEEN_FILE, 'r') as f:
    seen_ids = set(line.strip() for line in f if line.strip())

print(f"Loaded {len(seen_ids)} seen IDs")

# The IDs we found from check_matches.py (first column)
match_ids = [
    '<447358704.2079724.1777174812697@mail.yahoo.com>',
    '<A96A8554-C098-401B-A8B6-9160A47930F8@yahoo.com>',
    '<B77DCD3B-6D50-4C6B-83E1-A97F7D5A7365@yahoo.com>',
    '<971B8381-E12D-4656-87AB-88A1B4CC3F69@yahoo.com>',
    '<FEBF73B2-6C8B-4067-9AC6-21FEC30673CB@yahoo.com>',
    '<15CC1F70-2732-487D-A164-DC0A0F290DD4@yahoo.com>',
    '<1836520306.1730379.1777006089891@mail.yahoo.com>',
    '<1928014544.1729278.1777003638816@mail.yahoo.com>',
    '<B51F05DD-43A8-4F4C-AE3B-314BC4FD9DC6@yahoo.com>',
    '<EBE2D56D-D20E-44E1-9C73-470A1459569E@yahoo.com>',
    '<4384A41E-291B-4CFD-B412-302CA3B1E018@yahoo.com>',
    '<0100019dae14e8ad-8846d7f1-d9cc-4c9c-9054-efdff93c0168-000000@email.amazonses.com>',
    '<0100019dae11d25d-825a87eb-6c4c-48ba-8ad7-4ae235605be0-000000@email.amazonses.com>',
    '<487FDF8E-A997-44B4-88D9-F93713F51EE7@yahoo.com>',
    '<CC9DE714-CEC8-4F11-B450-69269603F8DB@yahoo.com>',
    '<671A1CB8-FB78-40C3-8838-1C1D299CD987@yahoo.com>'
]

print("\nChecking each match ID against seen set:")
for msg_id in match_ids:
    if msg_id in seen_ids:
        print(f"  {msg_id}: SEEN")
    else:
        print(f"  {msg_id}: NOT SEEN")

# Also, let's see how many of the seen IDs are in our match set
seen_and_match = seen_ids.intersection(set(match_ids))
print(f"\nNumber of seen IDs that are in match set: {len(seen_and_match)}")
print(f"Number of match IDs total: {len(match_ids)}")