import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

st.set_page_config(page_title="Smart Water Consumption Prediction", layout="wide")

# -------------------------------
# Project root
# -------------------------------
project_root = os.path.abspath(os.path.join(__file__, "..", "..", "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.predict_next_month_TC import call_predict_next_month_total_consumption

# -------------------------------
# Load data
# -------------------------------
data_dir = os.path.join(project_root, "data")
file_name = "clean_incidencies_comptadors_intelligents.parquet"
data_path = os.path.join(data_dir, file_name)

@st.cache_data
def load_data():
    return pd.read_parquet(data_path)

df = load_data()

# -------------------------------
# Initial input
# -------------------------------
st.title("💧 Smart Water Consumption Prediction")
poliza = st.text_input("Enter your POLIZA_SUMINISTRO:", "")

if st.button("Run Prediction"):
    if poliza.strip() == "":
        st.error("Please enter a valid POLIZA_SUMINISTRO.")
    else:
        try:
            total_pred, forecast_df, df_extended = call_predict_next_month_total_consumption(df, poliza)
            
            # Store in session_state to persist across reruns
            st.session_state['poliza'] = poliza
            st.session_state['df_extended'] = df_extended
            st.session_state['total_pred'] = total_pred

        except Exception as e:
            st.error(f"Error: {e}")
if 'df_extended' in st.session_state:

    df_extended = st.session_state['df_extended']
    total_pred = st.session_state['total_pred']

    # --- Compute last year's average daily consumption ---
    one_year_ago = df_extended["FECHA"].max() - pd.Timedelta(days=365)
    last_year_data = df_extended[df_extended["FECHA"] > one_year_ago]

    if not last_year_data.empty:
        avg_daily_last_year = last_year_data["CONSUMO_REAL"].mean()
        forecast_days = 30
        expected_avg = avg_daily_last_year * forecast_days

        if total_pred > expected_avg:
            st.warning(
                f"⚠️ Oh no! Your predicted consumption ({total_pred:.2f} liters) "
                f"is above your average last year ({expected_avg:.2f} liters). "
                "Try to reduce water usage where possible!"
            )
        else:
            st.success(
                f"🎉 Great! Your predicted consumption ({total_pred:.2f} liters) "
                f"is below your average last year ({expected_avg:.2f} liters). "
                "Keep up the good work conserving water!"
            )

# -------------------------------
# Display results if prediction exists
# -------------------------------
if 'df_extended' in st.session_state:

    col1, col2 = st.columns([0.35, 0.65])

    # -------------------------------
    # Left column: Bill info
    # -------------------------------
    with col1:
        st.header("How your water bill is calculated")

        with st.expander("1️⃣ Water Supply (Domestic Usage)"):
            st.markdown("""
            The **water supply** part of your bill depends on the number of cubic meters (m³) consumed.
            Aigües de Barcelona applies **progressive pricing**:

            | Tier | Monthly consumption | Price (€/m³) |
            |------|-------------------|---------------|
            | 0‑6 m³             | €0.8000 |
            | 7‑9 m³             | €1.6002 |
            | 10‑15 m³           | €2.4894 |
            | 16‑18 m³           | €3.3189 |
            | >18 m³             | €4.1486 |
            """)

        with st.expander("2️⃣ Water Canon (Government Tax)"):
            st.markdown("""
            - **Water Canon**: collected by the Catalan Water Agency (ACA).  
            - Depends on consumption thresholds.  
            - Example: ~€0.4936 per m³.
            """)

        with st.expander("3️⃣ Sewerage & Waste Fees"):
            st.markdown("""
            - **Sewerage fee**: maintenance of the sewer network.  
            - **Waste collection (TMTR, etc.)**: metropolitan fee.  
            - Fees are usually fixed or household-category based.
            """)

        with st.expander("4️⃣ VAT (10%) & Example Bill"):
            st.markdown(f"""
            - **VAT (IVA)**: 10% on supply + canon.  
            - **Example** (bi-monthly, ~14 m³ consumption):
                - Supply: €30.94  
                - Water Canon: €6.91  
                - Sewerage & Waste: €15.36  
                - VAT: €3.09  
                - **Total** ≈ €66.49
            """)

    # -------------------------------
    # Right column: Last X days consumption with slider
    # -------------------------------
    with col2:
        st.header("📊 Historical Consumption")

        # Slider to select period (days)
        days_to_show = st.slider(
            "Select number of days to visualize:",
            min_value=30,   # minimum 1 month
            max_value=365,  # maximum 12 months
            value=120,      # default 4 months
            step=15
        )

        df_extended = st.session_state['df_extended']
        filtered_df = df_extended[df_extended["FECHA"] > df_extended["FECHA"].max() - pd.Timedelta(days=days_to_show)]

        fig, ax = plt.subplots(figsize=(10,4))
        sns.lineplot(data=filtered_df, x="FECHA", y="CONSUMO_REAL", ax=ax, marker="o")
        ax.set_xlabel("Date")
        ax.set_ylabel("Consumption (litres)")
        ax.set_title(f"Water Consumption Last {days_to_show} Days")
        st.pyplot(fig)
