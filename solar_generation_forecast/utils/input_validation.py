import pandas as pd

class DataValidator:
    def __init__(self, generation_df: pd.DataFrame, monthly_df: pd.DataFrame):
        self.generation_df = generation_df
        self.monthly_df = monthly_df

    def validate_hourly_generation(self):
        df = self.generation_df
        messages = []

        required_columns = {"Datetime", "Generation(MWh)"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            messages.append(f"🔴 Missing columns in Generation sheet: {', '.join(missing)}")
        else:
            messages.append("✅ All required columns are present in Generation sheet.")

            if not pd.api.types.is_datetime64_any_dtype(df["Datetime"]):
                try:
                    df["Datetime"] = pd.to_datetime(df["Datetime"])
                    messages.append("🟡 Converted 'Datetime' column to datetime format.")
                except Exception:
                    messages.append("🔴 Failed to convert 'Datetime' to datetime format.")

            if df["Generation(MWh)"].isnull().any():
                messages.append("🟡 Null values found in 'Generation(MWh)' column.")

        return messages

    def validate_monthly_total_generation(self):
        df = self.monthly_df
        messages = []

        if df is None:
            messages.append("🔴 No Monthly Total Generation DataFrame provided.")
            return messages

        required_columns = {
            "Month",
            "Monthly_Total_Generation_MWh",
            "Installed_Power_MW",
            "Licence_Power_MW"
        }

        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            messages.append(f"🔴 Missing columns in Monthly_Total_Generation sheet: {', '.join(missing)}")
        else:
            messages.append("✅ All required columns are present in Monthly_Total_Generation sheet.")

            if df["Monthly_Total_Generation_MWh"].isnull().any():
                messages.append("🟡 Null values found in 'Monthly_Total_Generation_MWh' column.")

            if df["Installed_Power_MW"][0] == None:
                messages.append("🟡 Null values found in 'Installed_Power_MW' column.")

            if df["Licence_Power_MW"][0] == None:
                messages.append("🟡 Null values found in 'Licence_Power_MW' column.")

        return messages