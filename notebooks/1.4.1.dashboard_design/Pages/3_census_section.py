import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
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
def load_data(date_filter=None):

    # Columns we actually need
    columns_to_load = ["FECHA", "SECCIO_CENSAL", "CONSUMO_REAL", "US_AIGUA_GEST"]
    
    # Load parquet with only these columns
    df = pd.read_parquet(data_path, columns=columns_to_load)
    
    df["FECHA"] = pd.to_datetime(df["FECHA"])
    if date_filter is not None:
        start_date, end_date = date_filter
        df = df[(df["FECHA"] >= start_date) & (df["FECHA"] <= end_date)]
    

    df["CONSUMO_REAL"] = pd.to_numeric(df["CONSUMO_REAL"], errors="coerce").astype("float32")
    if "SECCIO_CENSAL" in df.columns:
        df["SECCIO_CENSAL_STR"] = df["SECCIO_CENSAL"].apply(
            lambda x: str(int(x)).zfill(10) if pd.notna(x) else None
        ).astype("category")
    else:
        df["SECCIO_CENSAL_STR"] = None
    
    if "US_AIGUA_GEST" in df.columns:
        df["US_AIGUA_GEST"] = df["US_AIGUA_GEST"].astype("category")
    
    return df

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
# User input
# -------------------------------
seccio_codes_str = sorted(df["SECCIO_CENSAL_STR"].dropna().unique().tolist()) if "SECCIO_CENSAL_STR" in df.columns else []

user_input = st.sidebar.text_input("Enter SECCIO_CENSAL code:")
filtered_codes = [p for p in seccio_codes_str if p.startswith(user_input)] if user_input else seccio_codes_str

if user_input and len(filtered_codes) == 0:
    st.sidebar.error("Code not found in dataset. Check typos or residence.")
    st.stop()

codi_censal = st.sidebar.selectbox("Matching codes", filtered_codes)

date_range = st.sidebar.date_input("Select Date Range", [df["FECHA"].min(), df["FECHA"].max()])
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

# -------------------------------
# Filter data for section and date range
# -------------------------------
df_section = df[df["SECCIO_CENSAL_STR"] == codi_censal]
df_section = df_section[(df_section["FECHA"] >= start_date) & (df_section["FECHA"] <= end_date)].copy()

if df_section.empty:
    st.warning("No data for this section and date range.")
    st.stop()



with st.sidebar.expander("ℹ️ What does percentile mean?"):
    st.markdown(
        """ 
        Your **percentile** shows your census section's average water use compared to all sections in the city.
        
        **For example**: If your percentile is 74, this means your section uses more water than 74% of census sections.
        - **Higher percentile** = higher consumption relative to others.
        - **Lower percentile** = lower consumption compared to peers.

        """
 )
# -------------------------------
# Summary cards
# -------------------------------
total_consumption = df_section["CONSUMO_REAL"].sum()

avg_daily = (df_section.groupby("FECHA")["CONSUMO_REAL"].sum().mean())

section_daily = (
    df.groupby(["FECHA", "SECCIO_CENSAL_STR"])["CONSUMO_REAL"]
    .sum()
    .reset_index()
)

municipality_avg_ts = (
    section_daily.groupby("FECHA")["CONSUMO_REAL"]
    .mean()
    .reset_index()
    .rename(columns={"CONSUMO_REAL": "Municipality Avg"})
)

municipality_avg_daily_per_section = municipality_avg_ts[
    (municipality_avg_ts["FECHA"] >= start_date) & (municipality_avg_ts["FECHA"] <= end_date)
]["Municipality Avg"].mean()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div style='background:{PRIMARY_LIGHT};padding:12px;border-radius:10px;text-align:center;'><div style='color:{PRIMARY_DARK};font-weight:700'>💧 Total Consumption</div><div style='font-size:20px;font-weight:700;color:{TEXT_PRIMARY};margin-top:6px'>{total_consumption:.2f} m³</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='background:{SECONDARY_LIGHT};padding:12px;border-radius:10px;text-align:center;'><div style='color:{SECONDARY_DARK};font-weight:700'>📅 Avg per day</div><div style='font-size:20px;font-weight:700;color:{TEXT_PRIMARY};margin-top:6px'>{avg_daily:.2f} m³/day</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div style='background:{PRIMARY_LIGHT};padding:12px;border-radius:10px;text-align:center;'><div style='color:{PRIMARY_DARK};font-weight:700'>🏛 Municipality avg per day</div><div style='font-size:20px;font-weight:700;color:{TEXT_PRIMARY};margin-top:6px'>{municipality_avg_daily_per_section:.2f} m³/day</div></div>", unsafe_allow_html=True)

st.divider()

# -------------------------------
# Time series plot
# -------------------------------
st.subheader("Consumption over time — Section vs Municipality average")
full_dates = pd.date_range(start=start_date, end=end_date)
section_ts = (df_section.groupby("FECHA")["CONSUMO_REAL"].sum().reset_index().rename(columns={"CONSUMO_REAL": "Section"}))
combined = pd.merge(section_ts, municipality_avg_ts, on="FECHA", how="outer").sort_values("FECHA").fillna(0)


# Plot
fig_ts = px.line(
    combined,
    x="FECHA",
    y=["Section", "Municipality Avg"],
    labels={"value": "Consumption (m³)", "variable": "Series"},
    title=f"Section {codi_censal} vs Municipality Avg per Section"
)
fig_ts.update_traces(mode="lines+markers")
st.plotly_chart(fig_ts, use_container_width=True)


st.divider()

# -------------------------------
# Use type breakdown
# -------------------------------
st.subheader("Consumption breakdown by use type")
if "US_AIGUA_GEST" in df_section.columns:
    breakdown = df_section.groupby("US_AIGUA_GEST")["CONSUMO_REAL"].sum().reset_index()
    breakdown["pct"] = breakdown["CONSUMO_REAL"]/breakdown["CONSUMO_REAL"].sum()*100
    fig_pie = px.pie(breakdown, values="CONSUMO_REAL", names="US_AIGUA_GEST", hole=0.45)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# -------------------------------
# Ranking
# -------------------------------
st.subheader("How your section ranks")
row_mask = (df["FECHA"] >= start_date) & (df["FECHA"] <= end_date)
df_filtered = df.loc[row_mask, ["FECHA", "SECCIO_CENSAL_STR", "CONSUMO_REAL"]]

df_month = df_filtered 
if not np.issubdtype(df_month["FECHA"].dtype, np.datetime64):
    df_month["FECHA"] = pd.to_datetime(df_month["FECHA"])
df_month["SECCIO_CENSAL_STR"] = df_month["SECCIO_CENSAL_STR"].astype("category")

df_month["month"] = df_month["FECHA"].dt.to_period("M")
monthly = (
    df_month.groupby(["SECCIO_CENSAL_STR", "month"])["CONSUMO_REAL"]
    .sum()
    .reset_index()
)
ranking = (
    monthly.groupby("SECCIO_CENSAL_STR")["CONSUMO_REAL"]
    .mean()
    .reset_index()
    .rename(columns={"CONSUMO_REAL":"avg_monthly"})
)

# Your section mean
my_section_avg = ranking.loc[ranking["SECCIO_CENSAL_STR"] == codi_censal, "avg_monthly"].values[0]
peer_mean = ranking.loc[ranking["SECCIO_CENSAL_STR"] != codi_censal, "avg_monthly"].mean()
percent_diff = (my_section_avg - peer_mean) / peer_mean * 100
percentile = (ranking["avg_monthly"] < my_section_avg).mean() * 100
if percent_diff > 0:
    st.markdown(
        f"""<div style='background:#e3f2fd;padding:14px;border-radius:7px'>
        <b>💧 Your census section uses {percent_diff:.1f}% more water than similar sections.</b></div>""",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f"""<div style='background:#e3f2fd;padding:14px;border-radius:7px'>
        <b>💧 Your census section uses {abs(percent_diff):.1f}% less water than similar sections.</b></div>""",
        unsafe_allow_html=True
    )
st.markdown(f"""<div style='background:#fce4ec;padding:14px;border-radius:7px'>
    <b>📊 Your consumption is in the {percentile:.0f}th percentile citywide.</b></div>""", unsafe_allow_html=True)

st.divider()

# -------------------------------
# Savings estimator
# -------------------------------
st.subheader("Quick savings estimator & tips")
price_per_m3 = st.number_input("Approx. price per m³ (€)", value=1.50, step=0.1)
reductions = [5, 10, 20]
cols = st.columns(len(reductions))
for pct, col in zip(reductions, cols):
    reduced_m3 = total_consumption*(pct/100)
    saved = reduced_m3*price_per_m3
    col.markdown(f"<div style='background:{PRIMARY_LIGHT};padding:10px;border-radius:8px;text-align:center;'><div style='font-weight:700;color:{PRIMARY_DARK}'>{pct}%</div><div style='font-size:16px;font-weight:700;color:{TEXT_PRIMARY};margin-top:6px'>{reduced_m3:.2f} m³</div><div style='color:{TEXT_SECONDARY}'>≈ €{saved:.2f}</div></div>", unsafe_allow_html=True)

st.markdown("**Tips:**")
if "US_AIGUA_GEST" in df_section.columns:
    top_use = df_section.groupby("US_AIGUA_GEST")["CONSUMO_REAL"].sum().idxmax()
    top_pct = df_section.groupby("US_AIGUA_GEST")["CONSUMO_REAL"].sum().max()/df_section["CONSUMO_REAL"].sum()*100
    if top_pct>=50:
        st.markdown(f"- Most consumption ({top_pct:.0f}%) is from **{top_use}**.")
    elif top_pct>=30:
        st.markdown(f"- Top category **{top_use}** accounts for {top_pct:.0f}%.")
    else:
        st.markdown("- Consumption spread across categories — consider general water-saving measures.")
st.markdown("- Fix leaking taps and pipes.")
st.markdown("- Use water-efficient appliances and mindful gardening watering.")

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
