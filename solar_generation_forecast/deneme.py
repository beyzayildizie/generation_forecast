import streamlit as st
import pandas as pd
import numpy as np
import random
import datetime

from io import BytesIO

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import plotly.io as pio
from plotly.subplots import make_subplots

# Constants
ZERO = 0
ONE = 1
ONE_YEAR_HOURS = 8784
ONE_DAY_HOURS = 24
ONE_YEAR_MONTHS = 12
FORECAST_YEAR_UPPER_LIMIT = 100
INSTALLED_POWER_MW_UPPER_LIMIT = 1005.0
LICENCE_POWER_MW_UPPER_LIMIT = 1005.0
DIVISION_VALUE_FOR_GENERATION_MEAN = 250.0

# Stabilization of Graphics
pio.templates.default = "plotly"
pio.templates["plotly"].layout.font = dict(family='Montserrat', size=20, color='black')


#st.title("Hiiii, my dear darlingsss 🥳!!")
#st.header("Beyza's page")

st.title("Solar Generation Forecast 🌞")

st.header("Visit RATIO SIM 🏂")
st.markdown('[RATIO SIM](https://app.ratiosim.com/login)')

st.header("Let's forecast!")

st.header("1. Inputs")
st.markdown("Enter Capacity Factor such as 0.17. It means % 17")
capacity_factor = st.number_input(
    label="Capacity Factor (0 - 1)",
    min_value=0.0,
    max_value=1.0,
    value=0.22,
    step=0.01,
    format="%.2f"
)

installed_power_mw = st.number_input(
    label="Installed Power (MW)",
    min_value=0.0,
    max_value=INSTALLED_POWER_MW_UPPER_LIMIT,
    value=35.75,
    step=0.25,
    format="%.2f"
)

licence_power_mw = st.number_input(
    label="Licence Power (MW)",
    min_value=0.0,
    max_value=LICENCE_POWER_MW_UPPER_LIMIT,
    value=30.0,
    step=0.25,
    format="%.2f"
)

start_date = st.date_input(
    label="Start Date",
    value=datetime.date(2024, 1, 1)
)

forecast_year = st.number_input(
    label="Forecast Period",
    min_value=1,
    max_value=100,
    value=20,
    step=1
)

# Aylık üretim için input alanları oluşturuyoruz
months = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]

# Başlangıçta 0.0 değerlerini vereceğiz
monthly_generation = []

# Kullanıcıdan her ay için üretim değerini alıyoruz
for month in months:
    value = st.number_input(f"{month} Ayı Üretim (MWh)", min_value=0.0, value=0.0)
    monthly_generation.append(value)

# Veriyi bir DataFrame'e çeviriyoruz
df = pd.DataFrame(monthly_generation, columns=["Toplam Üretim (MWh)"], index=months)

# Tabloyu görselleştiriyoruz
st.dataframe(df)

yearly_degradation_rate = st.number_input(
    label="Yearly Degredation Rate (exp: 0.007 means %0.7)",
    min_value=0.0,
    max_value=1.0,
    value=0.007,
    step=0.001,
    format="%.4f"
)

EXPECTED_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
EXPECTED_COLUMNS_HOURLY = {"Datetime", "Generation(MWh)"}
EXPECTED_COLUMNS_MONTHLY = {
    "Month", "Monthly_Total_Generation_MWh", "Installed_Power_MW", "Licence_Power_MW"
}

def validate_datetime_format(datetime_series, expected_format):
    try:
        pd.to_datetime(datetime_series, format=expected_format, errors="raise")
        return False
    except ValueError:
        return True

def validate_hourly_generation(df):
    messages = []

    missing_columns = EXPECTED_COLUMNS_HOURLY - set(df.columns)
    if missing_columns:
        messages.append(f"🔴 Missing columns: {', '.join(missing_columns)}")
        return messages

    if (df["Generation(MWh)"] < ZERO).any():
        messages.append("🔴 Generation values must be positive.")

    if df["Datetime"].isna().any():
        messages.append("🔴 Some datetime entries are missing.")

    if validate_datetime_format(df["Datetime"], EXPECTED_DATETIME_FORMAT):
        messages.append("🔴 Incorrect datetime format. Use: YYYY-MM-DD HH:MM:SS")

    if len(df) != ONE_YEAR_HOURS:
        messages.append(f"🟡 Expected {ONE_YEAR_HOURS} rows, found {len(df)}.")

    if not messages:
        messages.append("✅ Hourly solar generation is valid.")
    return messages

def validate_monthly_generation(df):
    messages = []

    missing_columns = EXPECTED_COLUMNS_MONTHLY - set(df.columns)
    if missing_columns:
        messages.append(f"🔴 Missing columns: {', '.join(missing_columns)}")
        return messages

    try:
        installed_power = float(df["Installed_Power_MW"].iloc[0])
        licence_power = float(df["Licence_Power_MW"].iloc[0])
    except Exception:
        messages.append("🔴 Installed or licence power must be numeric.")
        return messages

    if installed_power < ZERO or installed_power > INSTALLED_POWER_MW_UPPER_LIMIT:
        messages.append(f"🔴 Installed power must be between {ZERO} and {INSTALLED_POWER_MW_UPPER_LIMIT} MW.")
    else:
        messages.append("✅ Installed power is valid.")

    if licence_power < ZERO or licence_power > installed_power:
        messages.append("🔴 Licence power must be between 0 and installed power.")
    else:
        messages.append("✅ Licence power is valid.")

    monthly_gen = df["Monthly_Total_Generation_MWh"]
    if len(monthly_gen) != ONE_YEAR_MONTHS:
        messages.append(f"🔴 There must be exactly {ONE_YEAR_MONTHS} months of total generation.")
    elif (monthly_gen < ZERO).any():
        messages.append("🔴 Monthly generation must be positive for all months.")
    else:
        messages.append("✅ Monthly total generation is valid.")

    return messages

st.title("🌞 Solar Generation Forecast - Excel Dosyası Yükle")

# Kullanıcıya açıklama
st.markdown("Lütfen aşağıdaki formatta iki sayfadan oluşan bir Excel dosyası yükleyin:")

# Örnek tablo formatlarını göster
with st.expander("📄 Sayfa 1: Generation"):
    st.markdown("""
    **Sayfa Adı:** `Generation`  
    Aşağıdaki gibi saatlik üretim verisi içermelidir:
    
    | Datetime           | Generation(MWh) |
    |--------------------|-----------------|
    | 2024-01-01 00:00:00| 0.00            |
    | 2024-01-01 01:00:00| 0.00            |
    | 2024-01-01 02:00:00| 0.00            |
    """)

with st.expander("📄 Sayfa 2: Monthly_Total_Generation"):
    st.markdown("""
    **Sayfa Adı:** `Monthly_Total_Generation`  
    Aşağıdaki gibi aylık toplam üretim ve kurulu güç bilgilerini içermelidir:
    
    | Month | Monthly_Total_Generation_MWh | Installed_Power_MW | Licence_Power_MW |
    |-------|-------------------------------|---------------------|------------------|
    | 1     | 1174.18                       | 9.99                | 10.39            |
    | 2     | 1487.68                       |                     |                  |
    """)

st.markdown("📥 Aşağıdaki butona tıklayarak örnek Excel şablonunu indirebilirsiniz:")

with open("template_generation_forecast.xlsx", "rb") as file:
    st.download_button(
        label="📄 Örnek Excel Şablonunu İndir",
        data=file,
        file_name="template_generation_forecast.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Excel dosyası yükle
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    try:
        excel_data = pd.read_excel(uploaded_file, sheet_name=None)
        required_sheets = {"Generation", "Monthly_Total_Generation"}
        missing_sheets = required_sheets - set(excel_data)
        if missing_sheets:
            st.error(f"🔴 Missing sheet(s): {', '.join(missing_sheets)}")
        else:
            # Generation sheet
            st.subheader("📊 Generation Sheet Validation")
            generation_df = excel_data["Generation"]
            st.dataframe(generation_df.head())
            for msg in validate_hourly_generation(generation_df):
                st.success(msg) if "✅" in msg else st.warning(msg) if "🟡" in msg else st.error(msg)

            # Monthly_Total_Generation sheet
            st.subheader("📆 Monthly Total Generation Sheet Validation")
            monthly_df = excel_data["Monthly_Total_Generation"]
            st.dataframe(monthly_df.head())
            for msg in validate_monthly_generation(monthly_df):
                st.success(msg) if "✅" in msg else st.warning(msg) if "🟡" in msg else st.error(msg)

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")


# Curtailment hesabı
curtailment_generation_source = generation_df["Generation(MWh)"] - licence_power_mw
curtailment_generation_source = curtailment_generation_source.clip(lower=0)  # Negatifleri sıfırla

# Net üretim
net_generation_source = generation_df["Generation(MWh)"] - curtailment_generation_source

# Toplamlar
total_generation_source = generation_df["Generation(MWh)"].sum()
total_curtailment_generation_source = curtailment_generation_source.sum()
total_net_generation_source = net_generation_source.sum()

# Rasyolar
curtailment_ratio_generation_source = 100 * (total_curtailment_generation_source / total_generation_source)
capacity_factor_for_mechanic_plant_generation_source = 100 * (total_generation_source / (len(generation_df) * installed_power_mw))
capacity_factor_for_electricity_plant_generation_source = 100 * (total_net_generation_source / (len(generation_df) * licence_power_mw))

hourly_analysis_metrics = {
    "Metric": [
        "Curtailment Ratio (%)",
        "Capacity Factor (%) for Mechanic Plant",
        "Capacity Factor (%) for Electricity Plant"
    ],
    "Value": [
        round(curtailment_ratio_generation_source, 2),
        round(capacity_factor_for_mechanic_plant_generation_source, 2),
        round(capacity_factor_for_electricity_plant_generation_source, 2)
    ]
}

df_metrics = pd.DataFrame(hourly_analysis_metrics)

# Streamlit'te tablonun görüntülenmesi
st.write("### Generation Source Metrics")
st.dataframe(df_metrics)  # Bu, interaktif tabloyu ekler

# Eğer daha basit bir format istiyorsanız, şu şekilde de gösterebilirsiniz:
# st.write(df_metrics)  # Bu, daha düz bir tablo sağlar