import streamlit as st
import pandas as pd
import datetime

from utils.input_validation import DataValidator

from pathlib import Path

# markdown dosyasının yolu (bu örnekte relative path kullanılıyor)
md_path = Path(__file__).parent / "markdown" / "generation.md"

# markdown içeriğini oku
with open(md_path, "r", encoding="utf-8") as f:
    md_content_generation = f.read()

# içeriği streamlit ile göster
# st.markdown(md_content, unsafe_allow_html=True)

# Sabitler
INSTALLED_POWER_MW_UPPER_LIMIT = 500.0
LICENCE_POWER_MW_UPPER_LIMIT = 500.0

EXPECTED_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
EXPECTED_COLUMNS_HOURLY = {"Datetime", "Generation(MWh)"}
EXPECTED_COLUMNS_MONTHLY = {
    "Month", "Monthly_Total_Generation_MWh", "Installed_Power_MW", "Licence_Power_MW"
}

class InputPage:

    def __init__(self):
        self.init_state()

    def init_state(self):
        default_values = {
            "capacity_factor": None,
            "consider_cf" : False,
            "installed_power_mw": None,
            "licence_power_mw": None,
            "start_date": None,
            "forecast_year": None,
            "monthly_generation": [],
            "yearly_degradation_rate": None,
            "uploaded_file": None,
            "excel_data": {}
        }

        for key, value in default_values.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def render_inputs(self):
        st.header("1. Inputs")
        st.markdown("Enter Capacity Factor such as 0.17. It means % 17")

        self.capacity_factor = st.number_input(
            label="Capacity Factor (0 - 1)",
            min_value=0.0,
            max_value=1.0,
            value=0.22,
            step=0.01,
            format="%.2f"
        )
        self.consider_cf = st.checkbox(
            label="Kapasite Faktörü Hesaplamaya Dahil Edilsin mi?",
            value=True  # varsayılan olarak seçili
)


        self.installed_power_mw = st.number_input(
            label="Installed Power (MW)",
            min_value=0.0,
            max_value=INSTALLED_POWER_MW_UPPER_LIMIT,
            value=35.75,
            step=0.25,
            format="%.2f"
        )

        self.licence_power_mw = st.number_input(
            label="Licence Power (MW)",
            min_value=0.0,
            max_value=LICENCE_POWER_MW_UPPER_LIMIT,
            value=30.0,
            step=0.25,
            format="%.2f"
        )

        self.start_date = st.date_input(
            label="Start Date",
            value=datetime.date(2024, 1, 1)
        )

        self.forecast_year = st.number_input(
            label="Forecast Period",
            min_value=1,
            max_value=100,
            value=20,
            step=1
        )

        # Aylık üretim
        months = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        self.monthly_generation = []
        for month in months:
            value = st.number_input(f"{month} Ayı Üretim (MWh)", min_value=0.0, value=0.0)
            self.monthly_generation.append(value)

        df = pd.DataFrame(self.monthly_generation, columns=["Toplam Üretim (MWh)"], index=months)
        st.dataframe(df)

        self.yearly_degradation_rate = st.number_input(
            label="Yearly Degredation Rate (exp: 0.007 means %0.7)",
            min_value=0.0,
            max_value=1.0,
            value=0.007,
            step=0.001,
            format="%.4f"
        )

    def render_template_info(self):
        st.title("🌞 Solar Generation Forecast - Excel Dosyası Yükle")

        st.markdown("Lütfen aşağıdaki formatta iki sayfadan oluşan bir Excel dosyası yükleyin:")

        with st.expander("📄 Sayfa 1: Generation"):
            st.markdown(md_content_generation)

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
        with open("inputs/template_generation_forecast.xlsx", "rb") as file:
            st.download_button(
                label="📄 Örnek Excel Şablonunu İndir",
                data=file,
                file_name="inputs/template_generation_forecast.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    def render_file_upload_and_validation(self):
        self.uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
        if self.uploaded_file:
            try:
                self.excel_data = pd.read_excel(self.uploaded_file, sheet_name=None)
                required_sheets = {"Generation", "Monthly_Total_Generation"}
                missing_sheets = required_sheets - set(self.excel_data)
                if missing_sheets:
                    st.error(f"🔴 Missing sheet(s): {', '.join(missing_sheets)}")
                else:
                    st.subheader("📊 Generation Sheet Validation")
                    generation_df = self.excel_data["Generation"]
                    st.dataframe(generation_df.head())

                    st.subheader("📆 Monthly Total Generation Sheet Validation")
                    monthly_df = self.excel_data["Monthly_Total_Generation"]
                    st.dataframe(monthly_df.head())

                    validator = DataValidator(generation_df = generation_df,monthly_df = monthly_df)
                    for msg in validator.validate_hourly_generation():
                        st.success(msg) if "✅" in msg else st.warning(msg) if "🟡" in msg else st.error(msg)
                    for msg in validator.validate_monthly_total_generation():
                        st.success(msg) if "✅" in msg else st.warning(msg) if "🟡" in msg else st.error(msg)

            except Exception as e:
                st.error(f"⚠️ An error occurred: {e}")

    def save_inputs_to_session_state(self):
        st.session_state["capacity_factor"] = self.capacity_factor
        st.session_state["consider_cf"] = self.consider_cf
        st.session_state["installed_power_mw"] = self.installed_power_mw
        st.session_state["licence_power_mw"] = self.licence_power_mw
        st.session_state["start_date"] = self.start_date
        st.session_state["forecast_year"] = self.forecast_year
        st.session_state["monthly_generation"] = self.monthly_generation
        st.session_state["monthly_generation"] = self.monthly_generation
        st.session_state["yearly_degradation_rate"] = self.yearly_degradation_rate
        # st.session_state["uploaded_file"] = self.uploaded_file
        st.session_state["excel_data"] = self.excel_data


    def run(self):
        self.render_inputs()
        self.render_template_info()
        self.render_file_upload_and_validation()

        if self.uploaded_file and self.excel_data:
            self.save_inputs_to_session_state()
            st.success("✅ Tüm veriler başarıyla kaydedildi!")
        else:
            st.warning("🔶 Lütfen verileri doldurun ve Excel dosyasını yükleyin.")
        


# # Streamlit sayfa çalıştırıcısı
if __name__ == "__main__" or "pages/1_Data_Upload_and_Validation" in __name__:
    page = InputPage()
    page.run()
