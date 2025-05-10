import streamlit as st
import pandas as pd
import numpy as np
import random
import datetime

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


st.title("Hiiii, my dear darlingsss 🥳!!")
st.header("Beyza's page")

st.markdown('[RATIO SIM](https://app.ratiosim.com/login)')

st.markdown("Let's forecast generation 🌞🌬️!")

st.header("Inputs")
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