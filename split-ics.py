#!/usr/bin/env python3
"""
Split all.ics into per-day files named YYYYMMDD.ics
Usage: python3 split-ics.py
"""
import os
import re
import json

ICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'event', 'kubecon-2026')
input_file = os.path.join(ICS_DIR, 'all.ics')

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the VCALENDAR header (everything before the first VEVENT)
header_end = content.index('BEGIN:VEVENT')
header = content[:header_end].rstrip()

# Split into individual VEVENT blocks
raw_events = content.split('BEGIN:VEVENT')[1:]
events = ['BEGIN:VEVENT' + raw.split('END:VEVENT')[0] + 'END:VEVENT' for raw in raw_events]

# Group events by date (YYYYMMDD from DTSTART)
days = {}
for event in events:
    match = re.search(r'DTSTART[^:]*:(\d{8})', event)
    if not match:
        continue
    date_key = match.group(1)
    days.setdefault(date_key, []).append(event)

# Write each day to its own file
sorted_days = sorted(days.keys())
for date_key in sorted_days:
    day_events = days[date_key]
    ics_content = header + '\r\n' + '\r\n'.join(day_events) + '\r\nEND:VCALENDAR'
    out_file = os.path.join(ICS_DIR, f'{date_key}.ics')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(ics_content)
    print(f'Wrote {out_file} ({len(day_events)} events)')

# Also write a manifest (list of available day files) as JSON
manifest = [{'date': d, 'file': f'{d}.ics', 'count': len(days[d])} for d in sorted_days]
manifest_path = os.path.join(ICS_DIR, 'manifest.json')
with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)
print(f'\nWrote manifest.json with {len(sorted_days)} days')
