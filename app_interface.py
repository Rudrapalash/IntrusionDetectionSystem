import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="AI-IDS Monitor", layout="wide")

st.title("🛡️ AI-Powered Intrusion Detection System")
st.write("Real-time network analysis using your trained AI model.")

# Create two columns for the dashboard
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Live Traffic Stream")
    table_placeholder = st.empty()

with col2:
    st.subheader("Threat Metrics")
    metric_placeholder = st.empty()

# Real-time refresh loop
while True:
    try:
        # Read the log file created by the sniffer
        df = pd.read_csv("live_alerts.csv")
        
        # Display the last 15 packets
        table_placeholder.table(df.tail(15))
        
        # Calculate stats
        total = len(df)
        attacks = len(df[df['Status'].str.contains("ATTACK")])
        
        with metric_placeholder:
            st.metric("Total Packets", total)
            st.metric("Attacks Blocked", attacks, delta_color="inverse")
            if attacks > 0:
                st.warning(f"High risk detected from {df.iloc[-1]['Source']}")
                
    except:
        st.info("Waiting for sniffer to generate data...")
    
    time.sleep(1) # Refresh UI every second