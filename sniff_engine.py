import pandas as pd
import joblib
from scapy.all import sniff, IP, TCP, UDP
import time
import os

# 1. Load the AI Model (XGBoost/RandomForest)
model = joblib.load('ids_model.pkl')

# 2. Setup a CSV to store live results for the Web UI
LOG_FILE = "live_alerts.csv"
if not os.path.exists(LOG_FILE):
    df = pd.DataFrame(columns=['Time', 'Source', 'Destination', 'Protocol', 'Status'])
    df.to_csv(LOG_FILE, index=False)

def analyze_packet(packet):
    if IP in packet:
        # Extract features (Must match your training columns)
        # For this example: ['destination port', 'flow duration', 'total fwd packets', 'total backward packets']
        dest_port = packet.dport if (TCP in packet or UDP in packet) else 0
        flow_duration = 0.1 # Real flow duration requires tracking flow start/end
        fwd_pkts = 1
        bwd_pkts = 0
        
        # Prepare data for model
        input_data = pd.DataFrame([[dest_port, flow_duration, fwd_pkts, bwd_pkts]], 
                                  columns=['destination port', 'flow duration', 'total fwd packets', 'total backward packets'])
        
        # AI Prediction
        prediction = model.predict(input_data)[0]
        status = "⚠️ ATTACK" if prediction == 1 else "✅ Normal"
        
        # Write to shared log file
        new_entry = pd.DataFrame([[time.strftime("%H:%M:%S"), packet[IP].src, packet[IP].dst, packet[IP].proto, status]])
        new_entry.to_csv(LOG_FILE, mode='a', header=False, index=False)
        
        if prediction == 1:
            print(f"🚨 ALERT: Intrusion Detected from {packet[IP].src}!")

print("🚀 IDS Sensor is LIVE. Monitoring network...")
sniff(filter="ip", prn=analyze_packet, store=0)