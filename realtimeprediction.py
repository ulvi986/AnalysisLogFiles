import psutil
import pandas as pd
from datetime import datetime
import time
import win32evtlog
import joblib
import os

# Model yüklə
model = joblib.load("risk_model.pkl")

log_file = "risk_log.txt"
# Whitelist – heç vaxt öldürülməyəcək proses adları (kiçik hərflə yaz)
whitelist = ["python.exe", "explorer.exe", "chatgpt.exe", "chrome.exe","code.exe"]

# Event log funksiyası — əlavə məlumatlarla
def get_detailed_event_logs(log_type="Security", event_ids=[4624, 4634, 4625], max_events=5):
    server = 'localhost'
    log_handle = win32evtlog.OpenEventLog(server, log_type)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    logs = []
    total = 0

    while total < max_events:
        records = win32evtlog.ReadEventLog(log_handle, flags, 0)
        if not records:
            break
        for event in records:
            if event.EventID in event_ids:
                logs.append({
                    "event_id": event.EventID,
                    "event_source": event.SourceName,
                    "event_type": event.EventType
                })
                total += 1
            if total >= max_events:
                break
    return logs

print("🟢 Risk real-time monitor başladı...\n")

while True:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_read = psutil.disk_io_counters().read_bytes
    disk_write = psutil.disk_io_counters().write_bytes
    process_list = [proc.name() for proc in psutil.process_iter(['name'])][:5]

    # Event logları oxu
    recent_events = get_detailed_event_logs()
    event_ids_str = ", ".join(str(e['event_id']) for e in recent_events)

    # Risk üçün features hazırla
    row = {
        'cpu_usage_percent': cpu_usage,
        'ram_usage_percent': ram_usage,
        'disk_read_bytes': disk_read,
        'disk_write_bytes': disk_write,
        'event_4625': 1 if any(e['event_id'] == 4625 for e in recent_events) else 0,
        'cmd_detected': 1 if any('cmd.exe' in p.lower() for p in process_list) else 0
    }

    df = pd.DataFrame([row])
    risk = model.predict(df)[0]

    if risk == 1:
        print(f"\n⛔ [{timestamp}] RİSK AŞKARLANDI!")
        print(f"🔺 CPU: {cpu_usage}% | RAM: {ram_usage}% | Proseslər: {process_list}")

        # Təhlükəli prosesləri bağla
                # Təhlükəli prosesləri bağla
        actions = []
        for proc in psutil.process_iter(['pid', 'name']):
            name = proc.info['name'].lower()
            if 'cmd.exe' in name and name not in whitelist:
                try:
                    psutil.Process(proc.info['pid']).kill()
                    actions.append(f"Killed {proc.info['name']} (PID {proc.info['pid']})")
                except Exception as e:
                    actions.append(f"Error killing {proc.info['name']}: {e}")


        # Ən çox CPU yeyən prosesi tap və bağla (cmd.exe olmasa da et)
        # Ən çox CPU yeyən prosesi tap və bağla
        try:
            high_cpu_proc = sorted(
                [p for p in psutil.process_iter(['pid', 'name', 'cpu_percent']) if p.info['pid'] != 0 and p.info['name'].lower() not in whitelist],
                key=lambda p: p.info['cpu_percent'],
                reverse=True
            )
            if high_cpu_proc:
                top_proc = high_cpu_proc[0]
                proc_obj = psutil.Process(top_proc.info['pid'])
                proc_obj.kill()
                action_msg = f"Killed high CPU process: {top_proc.info['name']} (PID {top_proc.info['pid']}, CPU: {top_proc.info['cpu_percent']}%)"
                actions.append(action_msg)
                print(f"⚠️ {action_msg}")
        except Exception as e:
            actions.append(f"Error killing high CPU process: {e}")
            print(f"❌ Error killing high CPU process: {e}")


        # Ən çox RAM yeyən prosesi tap və bağla
        try:
            high_ram_proc = sorted(
                [p for p in psutil.process_iter(['pid', 'name', 'memory_info']) 
                if p.info['pid'] != 0 and p.info['name'].lower() not in whitelist],
                key=lambda p: p.info['memory_info'].rss,
                reverse=True
            )
            if high_ram_proc:
                top_ram = high_ram_proc[0]
                proc_obj = psutil.Process(top_ram.info['pid'])
                proc_obj.kill()
                action_msg = f"Killed high RAM process: {top_ram.info['name']} (PID {top_ram.info['pid']}, RAM: {top_ram.info['memory_info'].rss // (1024 * 1024)} MB)"
                actions.append(action_msg)
                print(f"⚠️ {action_msg}")
        except Exception as e:
            actions.append(f"Error killing high RAM process: {e}")
            print(f"❌ Error killing high RAM process: {e}")




        # Log fayla yaz
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] RİSK AŞKARLANDI:\n")
            for e in recent_events:
                f.write(f"  Event ID: {e['event_id']} | Source: {e['event_source']} | Type: {e['event_type']}\n")
            f.write(f"  Risk Predicted: {risk}\n")
            for a in actions:
                f.write(f"  Action: {a}\n")
            f.write("-" * 50 + "\n")
    else:
        print(f"[{timestamp}] ✅ Risk yoxdur. CPU: {cpu_usage}% | RAM: {ram_usage}%")

    time.sleep(5)
