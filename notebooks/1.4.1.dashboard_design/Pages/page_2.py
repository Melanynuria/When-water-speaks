import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path


current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)
                    
from src.predict_next_month_TC import call_predict_next_month_total_consumption

st.set_page_config(page_title="Detection of anomalies",page_icon="🚨", layout="wide", initial_sidebar_state="expanded")

# Color palette
PRIMARY_LIGHT = "#A8D5E8"
PRIMARY_DARK = "#045A89"
SECONDARY_LIGHT = "#B3DFD8"
SECONDARY_DARK = "#036354"
SUCCESS = "#9AC98F"
TEXT_PRIMARY = "#1F3A4A"
TEXT_SECONDARY = "#6B7C8C"
BG_COLOR = "#F5F8FA"

st.markdown(
    f""" <h1 style='text-align: center; color: #050505; background-color:{PRIMARY_LIGHT}; 
    padding: 25px; border-radius: 10px;'>🚨 Detection of Consumption Anomalies</h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""<div style='text-align: center; font-size:1.15em; color:{TEXT_SECONDARY}; margin-bottom:25px; line-height:1.8;'>
        Identify unusual consumption patterns, detect risks before they appear,
        and <span style='color:{SECONDARY_DARK}; font-weight:bold;'>save money</span> 
        with intelligent anomaly detection. </div>
    """,
    unsafe_allow_html=True
)

st.divider()

@st.cache_data
def load_default_parquet():
    file ="clean_incidencies_comptadors_intelligents.parquet"
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    data_dir =os.path.join(base_dir, "data")
    sample_path=os.path.join(data_dir,file)
    df_ICI=pd.read_parquet(sample_path)
    return df_ICI

@st.cache_data(show_spinner=True)
def cached_forecast(df,poliza_id):
    total,forecast_df, df_extended=call_predict_next_month_total_consumption(df, poliza_id)
    return total, forecast_df, df_extended




st.sidebar.header("⚙️ Configuration")
data_source=st.sidebar.radio("Data",["Default file", "Load parquet file"],index=0)

if data_source=="Default file":
    df=load_default_parquet()
else:
    uploaded=st.sidebar.file_uploader("Load parquet", type=["parquet"])
    if uploaded is not None:
        df=pd.read_parquet(uploaded)
    else:
        st.stop()

polizas=df["POLIZA_SUMINISTRO"].unique().tolist()
user_input=st.sidebar.text_input("Introduce your invoice:")

if user_input:
    filtered_poliza=[p for p in polizas if p.startswith(user_input)]
else:
    filtered_poliza=polizas

if user_input and len(filtered_poliza)==0:
    st.sidebar.error("The invoice introduced does not exist in our dataset."
                     "Review that there are no typos or confirm that you reside in Barcelona")
    st.stop()

poliza_id= st.sidebar.selectbox("Matching invoices",filtered_poliza)
threshold=st.sidebar.slider("Anomaly threshold", 1.0,5.0,2.0,0.1)

with st.sidebar.expander("ℹ️ What is the threshold?"):
    st.markdown(
        """
            The *threshold* controls which points are considered anomalous:
            - **Low** values (1-2): detects more anomalies (more sensative)
            - **High** values (3-5): detects only very extreme anomalies
        """
        )
    
with st.sidebar.expander("💰 How can you use forecast anomalies to save money?"):
    st.markdown(
    """
        Anomalies in **forecasted consumption** can indicate:
        - 🔺 **Unexpected consumption increases** → could mean a poorly configured appliance or excessive use.
        - 🔻 **Sudden drops** → could indicate meter errors or outages.

        **How does this help you save money?**
        - If the model detects that your future consumption will be **higher than normal**, you can take action before the bill arrives.
        - You can adjust habits, check appliances or possible leaks.
        - Alerts allow you to avoid surprises and betetr control your consumption.

        Adjust threshold as you wish:
        - **Low threshold** → see more alerts and prevent sooner
        - **High threshold** → only very important alerts.

    """
) 

@st.cache_data
def detect_anomalies(df,poliza_id,threshold):
    total,forecast_df,df_extended= cached_forecast(df,poliza_id)

    df_analysis=df_extended.copy()
    #rolling statistics
    df_analysis["rolling_mean"]=df_analysis["CONSUMO_REAL"].rolling(window=7,min_periods=3).mean()
    df_analysis["rolling_std"]=df_analysis["CONSUMO_REAL"].rolling(window=7,min_periods=3).std()
    df_analysis["z_score"]=(df_analysis["CONSUMO_REAL"]-df_analysis["rolling_mean"])/df_analysis["rolling_std"]
    df_analysis["is_anomaly"]=df_analysis["z_score"].abs()>threshold
    anomalies=df_analysis[df_analysis["is_anomaly"]]

    #same with forecasted data
    df_forecasting=forecast_df.copy()
    df_forecasting=df_forecasting.merge(df_analysis[["FECHA","rolling_mean","rolling_std"]],on="FECHA",how="left")
    df_forecasting["forecast_z_score"]=((df_forecasting["CONSUMO_REAL"]-df_forecasting["rolling_mean"])/df_forecasting["rolling_std"])
    df_forecasting["forecast_is_anomaly"]=df_forecasting["forecast_z_score"].abs()>threshold
    anomalies_forecast=df_forecasting[df_forecasting["forecast_is_anomaly"] & df_forecasting["is_forecast"]]
    
    return df_analysis, anomalies, df_forecasting, anomalies_forecast


df_analysis,anomalies, df_forecasting, anomalies_forecast=detect_anomalies(df, poliza_id,threshold)

st.subheader(f"📊Results for invoice {poliza_id}")
col1,col2=st.columns(2)
with col1:
    st.metric("Historical anomalies", len(anomalies))
with col2:
    st.metric("Predicted anomalies",len(anomalies_forecast))

st.divider()

st.subheader("📈 Anomalies graph")
fig,ax= plt.subplots(figsize=(12,6))
sns.lineplot(data=df_analysis, x="FECHA", y="CONSUMO_REAL", label="Historical Consumption", ax=ax, color=PRIMARY_DARK)
sns.scatterplot(data=anomalies, x="FECHA", y="CONSUMO_REAL", color="red", label="Historical Anomaly", s=80, ax=ax)

sns.lineplot(data=df_forecasting, x="FECHA", y="CONSUMO_REAL", label="Forecasted Consumption", linestyle="--", ax=ax, color=SECONDARY_DARK)
sns.scatterplot(data=anomalies_forecast, x="FECHA", y="CONSUMO_REAL", color="orange", label="Forecast Anomaly", s=80, ax=ax)

ax.set_title(f"Detection of anomalies -- Inovice {poliza_id}")
ax.set_xlabel("Data")
ax.set_ylabel("Real Consumption")
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig)
st.divider()




st.subheader("📄 Latest anomalies detected")
st.write("### Historical")
st.dataframe(anomalies.tail(10))
st.write("### Forecast")
st.dataframe(anomalies_forecast.tail(10))


if st.sidebar.button("Clear cache"):
    st.cache_data.clear()
    st.experimental_rerun()