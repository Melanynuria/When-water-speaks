import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import sys
import os
import math

st.set_page_config(
    page_title="Water Consumption by Census Section",
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
    f"<h1 style='text-align: center; color: #050505; background-color:{PRIMARY_LIGHT}; padding: 25px;'> 🏙️ Water Consumption by Census Section</h1>",
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style='text-align: center; font-size:1.15em; color:{TEXT_SECONDARY}; margin-bottom:30px; line-height:1.8;'>
        Enter your <span style='color:{PRIMARY_DARK}; font-weight:bold;'>SECCIO_CENSAL</span> on the sidebar 
        to get more information of your census section's water consumption and see insights to reduce water usage.
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()
# -------------------------------
# User Input
# -------------------------------
if 'SECCIO_CENSAL' in df.columns:
    seccio_censal_codes = df['SECCIO_CENSAL'].unique().tolist()
    # Convert secció censal codes to strings (and pad with zeros if needed)
    seccio_censal_codes_str = [str(int(c)).zfill(10) for c in seccio_censal_codes if c is not None and not (isinstance(c, float) and math.isnan(c))]

else:
    seccio_censal_codes = []

user_input=st.sidebar.text_input("Introduce your SECCIO_CENSAL code:")

if user_input:
    filtered_codes=[p for p in seccio_censal_codes_str if p.startswith(user_input)]
else:
    filtered_codes=seccio_censal_codes

if user_input and len(filtered_codes)==0:
    st.sidebar.error("The invoice introduced does not exist in our dataset."
                     "Review that there are no typos or confirm that you reside in Barcelona")
    st.stop()

codi_censal= float(st.sidebar.selectbox("Matching codes",filtered_codes))

if codi_censal:
    exists_msg = ''
    if seccio_censal_codes:
        exists_msg = ('found in dataset' if codi_censal in seccio_censal_codes else 'There is no data available for this census section.')

date_range = st.sidebar.date_input(
    "Select Date Range",
    [df["FECHA"].min(), df["FECHA"].max()]
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    # If user picks only a single date, use it as both min and max
    start_date = end_date = date_range


# -------------------------------
# Consumption Trend by Use Type
# -------------------------------

if codi_censal in seccio_censal_codes:
    df_filtered = df[df["SECCIO_CENSAL"] == codi_censal].copy()

    df_filtered["FECHA"] = pd.to_datetime(df_filtered["FECHA"], errors="coerce")


# Apply date filter
if len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered["FECHA"] >= pd.to_datetime(start_date)) &
        (df_filtered["FECHA"] <= pd.to_datetime(end_date))
    ]

    df_filtered["CONSUMO_REAL"] = pd.to_numeric(df_filtered["CONSUMO_REAL"], errors="coerce")

    df_plot = df_filtered.dropna(subset=["FECHA", "US_AIGUA_GEST", "CONSUMO_REAL"])

    monthly_use = (
        df_plot
        .groupby([df_plot["FECHA"].dt.to_period("M"), "US_AIGUA_GEST"])["CONSUMO_REAL"]
        .sum()
        .reset_index()
    )

    monthly_use["FECHA"] = monthly_use["FECHA"].dt.to_timestamp()
    monthly_use = monthly_use.sort_values("FECHA")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=monthly_use,
        x="FECHA",
        y="CONSUMO_REAL",
        hue="US_AIGUA_GEST",
        marker="o",
        ax=ax
    )

    ax.set_title(f"Monthly Water Consumption by Use Type – Section {codi_censal}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Consumption (m³)")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)
    
    section_data = df_filtered[df_filtered["SECCIO_CENSAL"] == codi_censal]

    total_consumption = section_data["CONSUMO_REAL"].sum()
    average_daily = section_data["CONSUMO_REAL"].mean()

    # Cute box using your palette colors
    st.markdown(
    f"""
    <div style="
        background-color:{PRIMARY_LIGHT};
        border-radius:15px;
        padding:20px;
        box-shadow:0 4px 12px rgba(0,0,0,0.1);
        margin-top:10px;
        margin-bottom:20px;
    ">
        <h4 style="
            color:{PRIMARY_DARK};
            text-align:center;
            margin-bottom:20px;
            font-weight:600;
        ">
            💧 Water Consumption Summary
        </h4>
        <div style="
            display:flex;
            justify-content:space-around;
            gap:20px;
        ">
            <div style="
                background-color:{BG_COLOR};
                padding:15px;
                border-radius:12px;
                text-align:center;
                flex:1;
                box-shadow:0 2px 6px rgba(0,0,0,0.08);
            ">
                <p style="margin:0; color:{TEXT_PRIMARY}; font-size:14px;">Total Consumption</p>
                <p style="margin:5px 0 0 0; font-size:20px; font-weight:bold; color:{PRIMARY_DARK};">
                    {total_consumption:.2f} m³
                </p>
            </div>
            <div style="
                background-color:{BG_COLOR};
                padding:15px;
                border-radius:12px;
                text-align:center;
                flex:1;
                box-shadow:0 2px 6px rgba(0,0,0,0.08);
            ">
                <p style="margin:0; color:{TEXT_PRIMARY}; font-size:14px;">Average Daily</p>
                <p style="margin:5px 0 0 0; font-size:20px; font-weight:bold; color:{PRIMARY_DARK};">
                    {average_daily:.2f} m³/day
                </p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
    )

    st.divider()


    time_series = section_data.groupby("FECHA")["CONSUMO_REAL"].sum().reset_index()

    fig = px.line(
        time_series,
        x="FECHA",
        y="CONSUMO_REAL",
        title=f"Water Consumption Over Time for Section {codi_censal}"
    )

   
    muni_avg = df.groupby("FECHA")["CONSUMO_REAL"].mean().reset_index()
    fig.add_scatter(x=muni_avg["FECHA"], y=muni_avg["CONSUMO_REAL"],
                        mode="lines", name="Municipality Average")

    st.plotly_chart(fig, use_container_width=True)

    st.divider()


    st.markdown(
    f"""
    <div style="
        display:flex;
        flex-wrap:wrap;
        justify-content:space-around;
        gap:20px;
        margin-top:25px;
    ">
    """
    ,
        unsafe_allow_html=True
    )
    st.subheader("Water Consumption Breakdown by Use Type")

    # Aggregate consumption by category (US_AIGUA_GEST)
    usage_breakdown = (
        df_filtered.groupby("US_AIGUA_GEST")["CONSUMO_REAL"]
        .sum()
        .reset_index()
    )

    usage_breakdown = usage_breakdown.sort_values("CONSUMO_REAL", ascending=False)
    total_section_consumption = usage_breakdown["CONSUMO_REAL"].sum()

    # Compute percentages
    usage_breakdown["percentage"] = (
        usage_breakdown["CONSUMO_REAL"] / total_section_consumption * 100
    )

    for _, row in usage_breakdown.iterrows():
        category = row["US_AIGUA_GEST"]
        value = row["CONSUMO_REAL"]
        pct = row["percentage"]

        st.markdown(
            f"""
            <div style="
                background-color:{PRIMARY_LIGHT};
                padding:15px;
                border-radius:12px;
                width:250px;
                text-align:center;
                box-shadow:0 3px 10px rgba(0,0,0,0.1);
            ">
                <p style="font-size:14px; margin:0; color:{PRIMARY_DARK}; font-weight:bold;">
                    {category}
                </p>
                <p style="font-size:20px; margin:5px 0 0 0; color:{TEXT_PRIMARY}; font-weight:600;">
                    {value:.2f} m³
                </p>
                <p style="font-size:14px; color:{TEXT_SECONDARY}; margin:0;">
                    {pct:.1f}% of total
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
# -------------------------------
# Consumption Analysis by Census Section
# -------------------------------
st.subheader("Top 10 Census Sections by Water Consumption")
ici_census = df.groupby('SECCIO_CENSAL')['CONSUMO_REAL'].agg(['mean', 'sum', 'count']).reset_index()
ici_census = ici_census.sort_values('sum', ascending=False)

# Select top 10 census sections by total consumption
top_census = ici_census.nlargest(10, 'sum')
top_census["SECCIO_CENSAL"] = top_census["SECCIO_CENSAL"].astype(str)
top_census = top_census.sort_values("sum", ascending=False)
top_census["SECCIO_CENSAL"] = pd.Categorical(
    top_census["SECCIO_CENSAL"],
    categories=top_census["SECCIO_CENSAL"],
    ordered=True
)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(
    x='SECCIO_CENSAL',
    y='sum',
    data=top_census,
    ax=ax,
    order=top_census["SECCIO_CENSAL"] 
)

ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
ax.set_title('Top 10 Census Sections by Total Consumption')
ax.set_ylabel('Total Consumption (m³)')
ax.set_xlabel('Secció Censal')

st.pyplot(fig)




# -------------------------------
# Water-Saving Tips
# -------------------------------
st.sidebar.info(
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
