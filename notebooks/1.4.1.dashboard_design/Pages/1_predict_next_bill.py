import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

st.set_page_config(
    page_title="💧 Smart Water Consumption Prediction",
    layout="wide",
)

# -------------------------------
# Colors & styles
# -------------------------------
PRIMARY_LIGHT = "#A8D5E8"
PRIMARY_DARK = "#045A89"
SECONDARY_LIGHT = "#B3DFD8"
SECONDARY_DARK = "#036354"
SUCCESS = "#9AC98F"
TEXT_PRIMARY = "#1F3A4A"
TEXT_SECONDARY = "#6B7C8C"
BG_COLOR = "#F5F8FA"

# -------------------------------
# Project root
# -------------------------------
project_root = os.path.abspath(os.path.join(__file__, "..", "..", "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.predict_next_month_TC import call_predict_next_month_total_consumption
from src.billing import euros_per_m3, get_next_month_bill
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
# Page Title
# -------------------------------
st.markdown(
    f"<h1 style='text-align: center; color: #050505; background-color:{PRIMARY_LIGHT}; padding: 25px;'>💧 Smart Water Consumption Prediction</h1>",
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style='text-align: center; font-size:1.15em; color:{TEXT_SECONDARY}; margin-bottom:30px; line-height:1.8;'>
        Enter your <span style='color:{PRIMARY_DARK}; font-weight:bold;'>POLIZA_SUMINISTRO</span> below 
        to predict your next month's water consumption and see insights to reduce water usage.
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

polizas=df["POLIZA_SUMINISTRO"].unique().tolist()



# -------------------------------
# User input
# -------------------------------
# -------------------------------
# User input: POLIZA + Service Type
# -------------------------------
col1, col2 = st.columns([0.6, 0.4])


with col1:
    poliza = st.selectbox("Matching invoices",polizas)



with col2:
    service_type = st.selectbox(
        "Select your service type",
        options=["D", "C", "A"],
        format_func=lambda x: {"D": "Domestic", "C": "Commercial", "A": "Agricultural"}[x]
    )
    st.session_state['service_type'] = service_type

if st.button("Run Prediction"):
    if poliza.strip() == "":
        st.error("Please enter a valid POLIZA_SUMINISTRO.")
    else:
        try:
            total_pred, forecast_df, df_extended = call_predict_next_month_total_consumption(df, poliza)
            st.session_state['poliza'] = poliza
            st.session_state['df_extended'] = df_extended
            st.session_state['total_pred'] = total_pred
            st.session_state['service_type'] = service_type

        except Exception as e:
            st.error(f"Error: {e}")

# -------------------------------
# Show prediction feedback
# -------------------------------
if 'df_extended' in st.session_state:

    df_extended = st.session_state['df_extended']
    total_pred = st.session_state['total_pred']

    # Compute last year's average daily consumption
    one_year_ago = df_extended["FECHA"].max() - pd.Timedelta(days=365)
    last_year_data = df_extended[df_extended["FECHA"] > one_year_ago]

    if not last_year_data.empty:
        avg_daily_last_year = last_year_data["CONSUMO_REAL"].mean()
        forecast_days = 30
        expected_avg = avg_daily_last_year * forecast_days
        pct_change = ((total_pred - expected_avg) / expected_avg) * 100

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💧 Predicted Consumption", f"{total_pred:.2f} L")
        delta_sign = "🔺" if pct_change > 0 else "🔻"
        col2.metric("📊 Change vs Last Year", f"{pct_change:.1f}%", delta=f"{delta_sign}")
        estimated_bill = total_pred * 1.5  # Simple approximation, adjust if needed

        total_pred = st.session_state['total_pred']
        service_type = st.session_state['service_type']

        base_price = euros_per_m3(total_pred, service_type)
        estimated_bill = get_next_month_bill(base_price)

        col3.metric("💳 Estimated Bill", f"€{estimated_bill:.2f}")
        efficiency_msg = "✅ Efficient" if total_pred <= expected_avg else "⚠️ Above Average"
        col4.metric("⚡ Efficiency", efficiency_msg)

        # Warning/Success feedback
        if total_pred > expected_avg:
            st.warning(
                f"⚠️ Your predicted consumption ({total_pred:.2f} liters) "
                f"is above last year's average ({expected_avg:.2f} liters). Try to reduce water usage!"
            )
        else:
            st.success(
                f"🎉 Your predicted consumption ({total_pred:.2f} liters) "
                f"is below last year's average ({expected_avg:.2f} liters). Keep up the good work!"
            )


st.divider()

# -------------------------------
# Layout: Bill Info & Historical Consumption
# -------------------------------
if 'df_extended' in st.session_state:

    col1, col2 = st.columns([0.35, 0.65])

    with col1:
        st.markdown(f"<h3 style='color:{PRIMARY_DARK};'>💡 How your water bill is calculated</h3>", unsafe_allow_html=True)

        with st.expander("1️⃣ Water Supply (Domestic Usage)"):
            st.markdown(f"""
            The **water supply** depends on cubic meters consumed.
            Progressive pricing is applied:

            | Tier | Monthly consumption | Price (€/m³) |
            |------|-------------------|---------------|
            | 1|0‑6 m³             | €0.8000 |
            | 2| 7‑9 m³             | €1.6002 |
            | 3|10‑15 m³           | €2.4894 |
            | 4|16‑18 m³           | €3.3189 |
            | 5|>18 m³             | €4.1486 |
            """)

        with st.expander("2️⃣ Water Canon (Government Tax)"):
            st.markdown(f"""
            - Collected by the Catalan Water Agency (ACA).  
            - Depends on consumption thresholds (~€0.4936 per m³).
            """)

        with st.expander("3️⃣ Sewerage & Waste Fees"):
            st.markdown(f"""
            - Sewerage network maintenance  
            - Waste collection fees (TMTR etc.)  
            """)

        with st.expander("4️⃣ VAT (10%) & Example Bill"):
            st.markdown(f"""
            - VAT: 10% on supply + canon  
            - Example (bi-monthly, ~14 m³): Total ≈ €66.49
            """)

    with col2:
        st.markdown(f"<h3 style='color:{SECONDARY_DARK};'>📊 Historical & Predicted Consumption</h3>", unsafe_allow_html=True)

        # Slider for historical days
        days_to_show = st.slider(
            "Select number of days to visualize:",
            min_value=30,
            max_value=365,
            value=120,
            step=15
        )

        filtered_df = df_extended[df_extended["FECHA"] > df_extended["FECHA"].max() - pd.Timedelta(days=days_to_show)]

        fig, ax = plt.subplots(figsize=(10,4))
        sns.lineplot(data=filtered_df, x="FECHA", y="CONSUMO_REAL", ax=ax, marker="o", label="Actual", color=PRIMARY_DARK)

        # Overlay predicted values if available
        if 'forecast_df' in locals():
            sns.lineplot(data=forecast_df, x="FECHA", y="CONSUMO_REAL", ax=ax, marker="o", label="Predicted", color=SUCCESS)

        ax.set_title(f"Water Consumption Last {days_to_show} Days")
        ax.set_xlabel("Date")
        ax.set_ylabel("Consumption (litres)")
        ax.legend()
        sns.despine()
        st.pyplot(fig)

# -------------------------------
# Water-Saving Tips
# -------------------------------
st.info(
    "💡 Water-Saving Tips:\n"
    "- Take shorter showers.\n"
    "- Fix leaking taps and pipes.\n"
    "- Use water-efficient appliances.\n"
    "- Collect rainwater for gardening."
)

# -------------------------------
# Download Data
# -------------------------------
if 'df_extended' in st.session_state:
    st.download_button(
        label="📥 Download My Consumption Data",
        data=st.session_state['df_extended'].to_csv(index=False),
        file_name=f"consumption_{st.session_state['poliza']}.csv",
        mime="text/csv"
    )

st.divider()

# -------------------------------
# Footer
# -------------------------------
st.markdown(f"""
<div style="text-align: center; padding: 20px; color: #050505; font-size: 12px;">
<p>
👥 Team members of Datasplash: Melany Nuria Condori, Judit Barba, Laura Peñalver, Xènia Fàbrega, Ella Lanqvist and Irene García
<br>
📂 <strong>Github Repository:</strong> <a href="https://github.com/Melanynuria/When-water-speaks.git" target="_blank" style="color: #5B9CBF; font-weight: bold;">View on GitHub</a>
<br>
🔒 <strong>Data Privacy & Security:</strong> All consumption data is encrypted and processed securely.
<br>
📞 <strong>Support:</strong> <a href="mailto:contact@aiguesdebarcelona.cat" style="color: #5B9CBF; font-weight: bold;">contact@aiguesdebarcelona.cat</a>
<br>
© 2025 Aigües de Barcelona - Water Consumption Analytics Platform
</p>
</div>
""", unsafe_allow_html=True)
