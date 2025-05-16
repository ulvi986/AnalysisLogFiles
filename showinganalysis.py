import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

plt.style.use("seaborn-v0_8-muted")

st.set_page_config(page_title="Smart Risk Monitor", layout="wide")

st.title("🧠 Smart Risk Monitor Dashboard")

# Risk Log göstər
log_file = "risk_log.txt"
if os.path.exists(log_file):
    with open(log_file, "r", encoding="utf-8") as f:
        logs = f.read()
    st.subheader("📄 Risk Log Qeydləri")
    st.text_area("Log", logs, height=400)
else:
    st.warning("Hələ log faylı yaranmayıb...")

# system_data_with_labels.csv faylını göstər
if os.path.exists("system_data_with_labels.csv"):
    df = pd.read_csv("system_data_with_labels.csv")
    st.subheader("📊 Toplanmış Sistem Məlumatları")
    st.dataframe(df.tail(10))
else:
    st.info("CSV faylı hələ mövcud deyil.")

# Event ID qrafiki
if os.path.exists("security.csv"):
    df = pd.read_csv("security.csv")
    df["Time"] = pd.to_datetime(df["Time"])
    df["User"] = df["Message"].str.split('|').str[2].str.strip()
    df["Hour"] = df["Time"].dt.hour

    risk_ids = [4625, 4672, 5379, 4738, 4616, 4904, 4905]
    df_risk = df[df["Event ID"].isin(risk_ids)]

    event_hourly = df_risk.groupby(["Hour", "Event ID"]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(14, 7))

    width = 0.1  # hər bar üçün eni
    x = event_hourly.index
    offsets = [-0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3]  # fərqli Event ID-ləri yanaşı göstərmək üçün offsetlər

    for i, event_id in enumerate(event_hourly.columns):
        ax.bar(
            x + offsets[i % len(offsets)],  # yerdəyişmə
            event_hourly[event_id],
            width=width,
            label=f"Event {event_id}"
        )


    ax.set_title("Saatlara görə təhlükəli Event ID-lərin sayı", pad=15)
    ax.set_xlabel("Saat (0–23)")
    ax.set_ylabel("Hadisə sayı")
    ax.set_xticks(range(0, 24))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc="upper right", frameon=True)

    st.subheader("Təhlükəli Event ID-lərin Dağılım Qrafiki")
    st.pyplot(fig)
else:
    st.info("security.csv faylı hələ mövcud deyil.")
