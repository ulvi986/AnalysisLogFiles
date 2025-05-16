import psutil
import pandas as pd
from datetime import datetime
import time
import win32evtlog  # Windows event logları üçün

data = []

def get_event_logs(log_type="Security", event_ids=[4624, 4634, 4625], max_events=10):
    server = 'localhost'
    log_handle = win32evtlog.OpenEventLog(server, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = []
    total = 0

    while total < max_events:
        records = win32evtlog.ReadEventLog(log_handle, flags, 0)
        if not records:
            break
        for event in records:
            if event.EventID in event_ids:
                events.append(event.EventID)
                total += 1
            if total >= max_events:
                break
    return events

start_time = time.time()
duration = 5 * 60  # 15 dəqiqə = 900 saniyə

while time.time() - start_time < duration:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_read = psutil.disk_io_counters().read_bytes
    disk_write = psutil.disk_io_counters().write_bytes
    process_list = [proc.name() for proc in psutil.process_iter(['name'])][:5]  # ilk 5 aktiv proqram

    # Security logundan logon/logoff eventləri
    recent_event_ids = get_event_logs()
    recent_event_ids_str = ", ".join(str(eid) for eid in recent_event_ids)

    row = {
        'timestamp': timestamp,
        'cpu_usage_percent': cpu_usage,
        'ram_usage_percent': ram_usage,
        'disk_read_bytes': disk_read,
        'disk_write_bytes': disk_write,
        'active_programs': ", ".join(process_list),
        'event_ids': recent_event_ids_str
    }

    data.append(row)

    # Ekranda göstəricilər
    print(f"\n✅ Yeni qeyd ({timestamp})")
    print(f"CPU: {cpu_usage}% | RAM: {ram_usage}%")
    print(f"Disk Read: {disk_read} bytes | Disk Write: {disk_write} bytes")
    print(f"Proseslər: {row['active_programs']}")
    print(f"Event ID-lər: {recent_event_ids_str}")

    time.sleep(5)

# CSV-yə yaz
df = pd.DataFrame(data)
file_name = f"system_data_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
df.to_csv(file_name, index=False)

print(f"\n✅ Bütün məlumatlar saxlandı: {file_name}")
