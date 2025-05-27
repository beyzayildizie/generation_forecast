
import streamlit as st
from utils.input_analysis import InputDataAnalyzer

class InputDataAnalysisPage:
    def __init__(self):
        #st.set_page_config(page_title="Input Data Analysis", layout="wide")
        st.title("Input Data Analysis")
        self.check_data()

    def check_data(self):
        if "excel_data" not in st.session_state or not st.session_state["excel_data"]:
            st.error("❌ Gerekli veriler bulunamadı. Lütfen önce 'Data Upload and Validation' adımını tamamlayın.")
            st.stop()


    def sidebar_controls(self, excel_data):
        st.sidebar.subheader("🔍 İncelemek istediğiniz tabloyu seçin")
        data_keys = list(excel_data.keys())
        selected_key = st.sidebar.selectbox("Tablo Seç", data_keys)

        df = excel_data[selected_key]
        datetime_columns = [col for col in df.columns if "date" in col.lower() or "time" in col.lower()]
        datetime_col = st.sidebar.selectbox("Zaman Sütunu Seç (Opsiyonel)", [""] + datetime_columns)

        return selected_key, datetime_col

    def show_generation_metrics(self, analyzer, selected_key):
        df = analyzer.data[selected_key]
        
        if "Generation(MWh)" not in df.columns:
            st.info("⚠️ Bu tabloda 'Generation(MWh)' sütunu bulunamadığı için üretim metrikleri hesaplanamadı.")
            return

        st.subheader("📊 Üretim Metrikleri")
        col1, col2 = st.columns(2)
        with col1:
            installed_power = st.number_input("Kurulu Güç (MW)", min_value=0.1, value=50.0)
        with col2:
            licence_power = st.number_input("Lisans Gücü (MW)", min_value=0.1, value=45.0)

        metrics_df = analyzer.calculate_generation_metrics(df, installed_power, licence_power)
        st.dataframe(metrics_df, use_container_width=True)


    def run(self):
        st.title("📈 Input Data Analysis")

        # excel_data = st.session_state["excel_data"]
        
        # analyzer = InputDataAnalyzer(excel_data)

        # st.sidebar.subheader("🔍 İncelemek istediğiniz tabloyu seçin")
        # data_keys = list(excel_data.keys())
        # selected_key = st.sidebar.selectbox("Tablo Seç", data_keys)

        # df = excel_data[selected_key]
        # datetime_columns = [col for col in df.columns if "date" in col.lower() or "time" in col.lower()]
        # datetime_col = st.sidebar.selectbox("Zaman Sütunu Seç (Opsiyonel)", [""] + datetime_columns)

        # analyzer.plot_time_series(selected_key, datetime_col if datetime_col else None)

        excel_data = st.session_state["excel_data"]
        analyzer = InputDataAnalyzer(excel_data)

        selected_key, datetime_col = self.sidebar_controls(excel_data)
        analyzer.plot_time_series(selected_key, datetime_col if datetime_col else None)

        metrics_df, curtailment_ratio, capacity_factor_mechanic, capacity_factor_electricity = self.show_generation_metrics(analyzer, selected_key)
        st.dataframe(metrics_df)
        st.session_state["curtailment_ratio"] = curtailment_ratio
        st.session_state["capacity_factor_mechanic"] = capacity_factor_mechanic 
        st.session_state["capacity_factor_electricity"] = capacity_factor_electricity

        analyzer.handle_capacity_factor_input(st.session_state["capacity_factor_mechanic"], st.session_state["consider_cf"])



# Sayfa çalıştırma
if __name__ == "__main__":
    page = InputDataAnalysisPage()
    page.run()
