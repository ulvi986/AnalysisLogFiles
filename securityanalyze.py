import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("security.csv")
#print(df.info())
#print(df.isnull().sum())
#print(df["Event ID"].unique())
#print(df.head())
#df["Type"] = pd.to_numeric(df["Type"], errors='coerce')  # string-dirsə sayıya çevir

type_map = {
    8:"Success"
}
df["Type"] = df["Type"].map(type_map)
#print(df.head())
import pandas as pd

df = pd.read_csv("security.csv")
df["Time"] = pd.to_datetime(df["Time"])
df["User"] = df["Message"].str.split('|').str[2].str.strip()
df["Hour"] = df["Time"].dt.hour
night_logins = df[(df["Hour"] >= 0) & (df["Hour"] < 6)]

print("Gecə saatlarında giriş edənlər:")
print(night_logins["User"].value_counts())
print("Ən çox login edən istifadəçilər:")
print(df["User"].value_counts())
print(df["Event ID"].unique())

listrisk = []

for event, source,user,time in zip(df["Event ID"], df["Source"],df["User"],df["Time"]):
    if event in [4625,4672,5379,4738,4616,4904,4905]:
        listrisk.append([event, source,user,time])

df_risk = pd.DataFrame(listrisk, columns=["Event ID", "Source", "User","Time"])
summary = df_risk.groupby(["Event ID", "User"]).size().reset_index(name="Count")
print(summary)
print(df_risk)

"""
plt.figure(figsize=(10,6))
plt.plot(df_risk["Event ID"].unique(), label="Real qiymət")
plt.plot(df_risk["Time"].unique(), label="Proqnoz", linestyle='dashed')
plt.title("Real vs Proqnoz (Random Forest Regression)")
plt.xlabel("Müşahidə sayı")
plt.ylabel("Qiymət")
plt.legend()
plt.grid(True)
plt.show()
"""

# Tarixi datetime-ə çevirək və saat çıxaraq
df_risk["Time"] = pd.to_datetime(df_risk["Time"])
df_risk["Hour"] = df_risk["Time"].dt.hour

# Saat və Event ID-lərə görə qrupla
event_hourly = df_risk.groupby(["Hour", "Event ID"]).size().unstack(fill_value=0)

# Qrafiki çək
plt.figure(figsize=(12, 6))
for event_id in event_hourly.columns:
    plt.plot(event_hourly.index, event_hourly[event_id], label=f"Event {event_id}")

plt.title("Saatlara görə Event ID-lərin sayı")
plt.xlabel("Saat")
plt.ylabel("Hadisə sayı")
plt.xticks(range(0, 24))  # 0-dan 23-ə qədər saatlar
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
