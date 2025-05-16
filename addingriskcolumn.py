import pandas as pd

# Faylı yüklə
df = pd.read_csv("system_data.csv")  # Sənin orijinal fayl adın

# Yeni sütunlar əlavə et (features üçün)
df['event_4625'] = df['event_ids'].apply(lambda x: 1 if '4625' in str(x) else 0)
df['cmd_detected'] = df['active_programs'].apply(lambda x: 1 if 'cmd.exe' in str(x).lower() else 0)

# Risk Predicted qaydaları (simple heuristics)
def predict_risk(row):
    if (
        row['cpu_usage_percent'] > 50 or
        row['ram_usage_percent'] > 50 or
        row['disk_write_bytes'] > 1_000_000_000 or
        row['event_4625'] == 1 or
        row['cmd_detected'] == 1
    ):
        return 1
    return 0

# Yeni sütun əlavə et
df['Risk_Predicted'] = df.apply(predict_risk, axis=1)

# Yadda saxla
df.to_csv("system_data_with_labels.csv", index=False)
print("✅ Etiketlənmiş fayl yaradıldı: system_data_with_labels.csv")
