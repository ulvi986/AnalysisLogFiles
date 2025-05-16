import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Dataset-i yüklə
df = pd.read_csv("system_data_with_labels.csv")

# Feature engineering (event və process sütunlarından yeni binary sütunlar düzəldirik)
df['event_4625'] = df['event_ids'].apply(lambda x: 1 if '4625' in str(x) else 0)
df['cmd_detected'] = df['active_programs'].apply(lambda x: 1 if 'cmd.exe' in str(x).lower() else 0)

# Modelə lazım olan sütunlar
features = [
    'cpu_usage_percent',
    'ram_usage_percent',
    'disk_read_bytes',
    'disk_write_bytes',
    'event_4625',
    'cmd_detected'
]
X = df[features]
y = df['Risk_Predicted']

# Train/test böl
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model qur
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Qiymətləndirmə
y_pred = clf.predict(X_test)
print("📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Modeli yadda saxla
joblib.dump(clf, "risk_model.pkl")
print("✅ Model uğurla saxlandı: risk_model.pkl")
