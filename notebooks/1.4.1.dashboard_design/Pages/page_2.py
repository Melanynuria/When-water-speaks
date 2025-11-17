import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import os
import sys
from pathlib import Path

#import function from source
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

#page header
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


#side bar configuration
st.sidebar.header("⚙️ Configuration")
data_source=st.sidebar.radio("Data",["Default file", "Load parquet file"],index=0)

@st.cache_data
def load_default_parquet():
    file ="clean_incidencies_comptadors_intelligents.parquet"
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    data_dir =os.path.join(base_dir, "data")
    sample_path=os.path.join(data_dir,file)
    df_ICI=pd.read_parquet(sample_path)
    return df_ICI


if data_source=="Default file":
    df=load_default_parquet()
else:
    uploaded=st.sidebar.file_uploader("Upload parquet", type=["parquet"])
    if uploaded:
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
            - **High** values (3-5): detects only extreme anomalies
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
        - You can adjust habits, **check appliances** or **possible leaks**.
        - Alerts allow you to **avoid surprises** and better control your consumption.

        Adjust threshold as you wish:
        - **Low threshold** → see more alerts and prevent sooner
        - **High threshold** → only very important alerts.

    """
) 

#caching
@st.cache_data(show_spinner=True)
def cached_forecast(df,poliza_id):
    total,forecast_df, df_extended=call_predict_next_month_total_consumption(df, poliza_id)
    return total, forecast_df, df_extended

@st.cache_data
def compute_base(df,poliza_id):
    total,forecast_df,df_extended= cached_forecast(df,poliza_id)
    df_analysis=df_extended.copy()
    #rolling statistics
    df_analysis["rolling_mean"]=df_analysis["CONSUMO_REAL"].rolling(window=7,min_periods=3).mean()
    df_analysis["rolling_std"]=df_analysis["CONSUMO_REAL"].rolling(window=7,min_periods=3).std()
    return df_analysis,forecast_df

df_analysis,df_forecast=compute_base(df,poliza_id)


def detect_anomalies(df_analysis,df_forecast,threshold):
    df_analysis["z_score"]=(df_analysis["CONSUMO_REAL"]-df_analysis["rolling_mean"])/df_analysis["rolling_std"]
    df_analysis["is_anomaly"]=df_analysis["z_score"].abs()>threshold
    anomalies=df_analysis[df_analysis["is_anomaly"]]

    #same with forecasted data
    df_forecasting=df_forecast.copy()
    df_forecasting=df_forecasting.merge(df_analysis[["FECHA","rolling_mean","rolling_std"]],on="FECHA",how="left")
    df_forecasting["forecast_z_score"]=((df_forecasting["CONSUMO_REAL"]-df_forecasting["rolling_mean"])/df_forecasting["rolling_std"])
    df_forecasting["forecast_is_anomaly"]=df_forecasting["forecast_z_score"].abs()>threshold
    anomalies_forecast=df_forecasting[df_forecasting["forecast_is_anomaly"] & df_forecasting["is_forecast"]]
    
    return df_analysis, anomalies, df_forecasting, anomalies_forecast


df_analysis,anomalies, df_forecasting, anomalies_forecast=detect_anomalies(df_analysis, df_forecast,threshold)

#show results
st.subheader(f"📊Results for invoice {poliza_id}")
col1,col2=st.columns(2)

with col1:
    st.markdown(f"""<div style='background-color:{PRIMARY_LIGHT}; padding:20px; border-radius:12px; text-align:center;'>
        <h3 style='margin:0; color:{PRIMARY_DARK};'>Historical anomalies</h3>
        <p style='font-size:2em; font-weight:bold; color:{TEXT_PRIMARY}; margin:5px 0;'>{len(anomalies)}</p></div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div style='background-color:{SECONDARY_LIGHT}; padding:20px; border-radius:12px; text-align:center;'>
        <h3 style='margin:0; color:{SECONDARY_DARK};'>Predicted anomalies</h3>
        <p style='font-size:2em; font-weight:bold; color:{TEXT_PRIMARY}; margin:5px 0;'>{len(anomalies_forecast)}</p></div>
    """, unsafe_allow_html=True)

st.divider()

#plot anomalies
st.subheader("📈 Anomalies graph")

hist = df_analysis[df_analysis["is_forecast"] == False]
forecast = df_analysis[df_analysis["is_forecast"] == True]
fig = px.line(hist, x="FECHA", y="CONSUMO_REAL", labels={"CONSUMO_REAL":"Consumption"}, title=f"Invoice {poliza_id}")
fig.add_scatter(x=anomalies["FECHA"], y=anomalies["CONSUMO_REAL"], mode="markers", marker_color="red", name="Historical Anomaly")
fig.add_scatter(x=df_forecasting["FECHA"], y=df_forecasting["CONSUMO_REAL"], mode="lines", line=dict(dash="dashdot", color=PRIMARY_DARK, width=5), name="Forecasted Consumption")
fig.add_scatter(x=anomalies_forecast["FECHA"], y=anomalies_forecast["CONSUMO_REAL"], mode="markers", marker_color="orange", name="Forecast Anomaly")
st.plotly_chart(fig, use_container_width=True)
st.divider()


#Show lasts anomalies
#Only show basic information
hist_cols=["FECHA","CONSUMO_REAL","is_anomaly"]
forecast_cols=["FECHA","CONSUMO_REAL","forecast_z_score","forecast_is_anomaly"]
st.subheader("📄 Latest anomalies detected")
tab1,tab2=st.tabs(["Historical", "Forecast"])
def color_anomalies(val):
    return 'background-color: red; color:white' if val else ''

with tab1:
    df_clean_hist=anomalies[hist_cols].tail(10)
    st.dataframe(df_clean_hist.style.applymap(color_anomalies, subset=["is_anomaly"]))

with tab2:
    df_fore_clean=anomalies_forecast[forecast_cols].tail(10)
    st.dataframe(df_fore_clean.tail(10).style.applymap(color_anomalies, subset=["forecast_is_anomaly"]))


if st.sidebar.button("Clear cache"):
    st.cache_data.clear()
    st.experimental_rerun()