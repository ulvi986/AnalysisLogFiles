import win32evtlog
import csv
from datetime import datetime, timedelta

# Sistem və tarix ayarları
server = 'localhost'
log_type = 'Security'
start_time = datetime.now() - timedelta(days=7)

# Logu aç
hand = win32evtlog.OpenEventLog(server, log_type)
flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

events = []
while True:
    records = win32evtlog.ReadEventLog(hand, flags, 0)
    if not records:
        break
    for event in records:
        if event.TimeGenerated >= start_time:
            events.append(event)
        else:
            break  # 7 gündən köhnədirsə, dayandır

# CSV faylına yaz
with open("security.csv", "w", newline='', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Time", "Source", "Event ID", "Type", "Category", "Message"])

    for event in events:
        event_id = event.EventID & 0xFFFF  # Düzgün formatlı Event ID
        message = ' | '.join(event.StringInserts) if event.StringInserts else ""
        writer.writerow([
            event.TimeGenerated,
            event.SourceName,
            event_id,
            event.EventType,
            event.EventCategory,
            message
        ])
