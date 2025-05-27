# input_analysis.py

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

class InputDataAnalyzer:
    def __init__(self, data: dict):
        """
        data: {'sheet_name1': df1, 'sheet_name2': df2, ...}
        """
        self.data = data

    def plot_time_series(self, key: str, datetime_col: str = None):
        """
        Belirtilen sheet (key) içindeki veriyi zaman serisi olarak çizer.
        datetime_col verilmezse ilk datetime uygun sütun denenir.
        """
        if key not in self.data:
            st.warning(f"'{key}' tablosu bulunamadı.")
            return

        df = self.data[key].copy()

        # Tarih sütununu otomatik algıla
        if not datetime_col:
            possible_cols = ["date", "timestamp", "Datetime", "time"]
            datetime_col = next((col for col in df.columns if col.lower() in possible_cols), None)

        if datetime_col is None or datetime_col not in df.columns:
            st.warning("⏱ Zaman sütunu bulunamadı. Grafik çizilemiyor.")
            return

        df[datetime_col] = pd.to_datetime(df[datetime_col])
        df = df.set_index(datetime_col)

        fig, ax = plt.subplots(figsize=(10, 4))
        df.plot(ax=ax)
        ax.set_title(f"{key} - Zaman Serisi")
        ax.set_xlabel("Zaman")
        ax.set_ylabel("Değerler")
        ax.grid(True)

        st.pyplot(fig)

    def calculate_generation_metrics(self, generation_df, installed_power_mw, licence_power_mw):
        # Curtailment hesabı
        curtailment = generation_df["Generation(MWh)"] - licence_power_mw
        curtailment = curtailment.clip(lower=0)  # Negatifleri sıfırla

        # Net üretim
        net_generation = generation_df["Generation(MWh)"] - curtailment

        # Toplamlar
        total_generation = generation_df["Generation(MWh)"].sum()
        total_curtailment = curtailment.sum()
        total_net_generation = net_generation.sum()

        # Rasyolar
        curtailment_ratio = 100 * (total_curtailment / total_generation)
        capacity_factor_mechanic = 100 * (total_generation / (len(generation_df) * installed_power_mw))
        capacity_factor_electricity = 100 * (total_net_generation / (len(generation_df) * licence_power_mw))

        # Sonuçları DataFrame olarak döndür
        metrics = {
            "Metric": [
                "Curtailment Ratio (%)",
                "Capacity Factor (%) for Mechanic Plant",
                "Capacity Factor (%) for Electricity Plant"
            ],
            "Value": [
                round(curtailment_ratio, 2),
                round(capacity_factor_mechanic, 2),
                round(capacity_factor_electricity, 2)
            ]
        }
        metrics_df = pd.DataFrame(metrics)

        # Hem tabloyu hem de üç rasyoyu ayrı olarak döndür
        return metrics_df, curtailment_ratio, capacity_factor_mechanic, capacity_factor_electricity

    
    def handle_capacity_factor_input(self,capacity_factor_mechanic,consider_cf):

        if consider_cf == "Hayır":
            st.session_state["capacity_factor_ratio"] = 1
            #st.info("📌 Kapasite faktörü hesaba katılmayacak. Oran = 1")
            return

        try:
            user_value = float(st.session_state["capacity_factor_ratio"].replace(",", "."))
            if user_value in [0, 1]:
                st.session_state["capacity_factor_ratio"] = 1
                st.info("📌 Varsayılan oran kullanılacak (1)")
            else:
                ratio = (user_value * 100) / capacity_factor_mechanic
                st.session_state["capacity_factor_ratio"] = ratio
                #st.success(f"✅ Kapasite faktörü oranı: {round(ratio, 3)}")
        except (ValueError, AttributeError):
            st.warning("⚠️ Lütfen geçerli bir sayı girin.")

