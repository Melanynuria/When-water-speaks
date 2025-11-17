import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns

st.set_page_config(
    page_title="When Water Speaks",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color palette
PRIMARY_LIGHT = "#A8D5E8"
PRIMARY_DARK = "#045A89"
SECONDARY_LIGHT = "#B3DFD8"
SECONDARY_DARK = "#036354"
SUCCESS = "#9AC98F"
TEXT_PRIMARY = "#1F3A4A"
TEXT_SECONDARY = "#6B7C8C"
BG_COLOR = "#F5F8FA"

#sidebar 
with st.sidebar.expander("📋 Pages Information"):
    st.markdown("""
    ### Page 1: 📊 Predict Your Water Bill
    Estimate next month's water bill
    
    ### Page 2: 🚨 Anomaly Detection
    Get alerts for unusual patterns
    
    ### Page 3: 💧 My Water Consumption
    View household consumption by census section
    """)

st.markdown(
    "<h1 style='text-align: center; color: #050505; background-color:#A8D5E8; padding: 25px;'>👋 Welcome to When Water Speaks </h1>",
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div style='text-align: center; font-size:1.15em; color:{TEXT_SECONDARY}; margin-bottom:30px; line-height:1.8;'>
        <span style='color:{PRIMARY_DARK}; font-weight:bold; font-size:1.2em;'>Track</span> your water consumption, 
        <span style='color:{SECONDARY_DARK}; font-weight:bold; font-size:1.2em;'>predict your bills</span>, 
        and <span style='color:{SUCCESS}; font-weight:bold; font-size:1.2em;'>stay informed</span> with smart insights.<br>
        <span style='font-size:1.1em; margin-top:10px;'>Manage your water usage effortlessly. 💧</span>
    </div>
    """, unsafe_allow_html=True
)

st.divider()

st.markdown("<h2 style='text-align: center; color: #050505;'>🎯 Main Project Objectives</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style='background-color:{PRIMARY_LIGHT}; padding:20px; border-radius:10px; margin-bottom:15px;'>
        <h3 style='color:{PRIMARY_DARK}; margin-top:0;'>🔍 Anomaly Detection</h3>
        <p style='color:{TEXT_PRIMARY};'>Identify unusual consumption patterns (leaks, fraud, meter issues)</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background-color:{SECONDARY_LIGHT}; padding:20px; border-radius:10px;'>
        <h3 style='color:{SECONDARY_DARK}; margin-top:0;'>📈 Pattern Analysis</h3>
        <p style='color:{TEXT_PRIMARY};'>Understand consumption trends across seasons and time periods</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color:{SECONDARY_LIGHT}; padding:20px; border-radius:10px; margin-bottom:15px;'>
        <h3 style='color:{SECONDARY_DARK}; margin-top:0;'>⚡ Efficiency Improvement</h3>
        <p style='color:{TEXT_PRIMARY};'>Optimize water management and reduce waste</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background-color:{PRIMARY_LIGHT}; padding:20px; border-radius:10px;'>
        <h3 style='color:{PRIMARY_DARK}; margin-top:0;'>💡 Data-Driven Insights</h3>
        <p style='color:{TEXT_PRIMARY};'>Support decision-making for better resource allocation</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.markdown("<h2 style='text-align: center; color: #050505;'>🌍 Sustainability Alignment</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info("🌊 **SDG 6: Clean Water & Sanitation**\n\nPromote responsible water consumption", icon="💧")

with col2:
    st.info("🏙️ **SDG 11: Sustainable Cities**\n\nSupport urban water management", icon="🌱")

with col3:
    st.info("🌡️ **SDG 13: Climate Action**\n\nReduce environmental impact through efficiency", icon="🌿")

st.markdown(
    f"""
    <div style='text-align: center; margin-top: 20px;'>
        <a href='https://sdgs.un.org/es/goals' target='_blank' 
           style='display: inline-block; padding: 12px 24px; background-color: {PRIMARY_DARK}; 
                  color: white; text-decoration: none; border-radius: 8px; 
                  font-weight: bold; transition: 0.3s;'
           onmouseover="this.style.backgroundColor='{SECONDARY_DARK}'"
           onmouseout="this.style.backgroundColor='{PRIMARY_DARK}'">
            🌍 Learn More About United Nations SDGs
        </a>
    </div>
    """, unsafe_allow_html=True
)
st.divider()

st.markdown("<h2 style='text-align: center; color: #050505;'>💰 Impact & Benefits</h2>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💧 Water Savings", "↓ 15-20%", "By identifying anomalies")

with col2:
    st.metric("🌱 Environment", "Protected", "Resource preservation")

with col3:
    st.metric("💳 Costs", "↓ Lower bills", "Through efficiency")

with col4:
    st.metric("📊 Accuracy", "↑ Improved", "Billing & detection")

st.divider()




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
