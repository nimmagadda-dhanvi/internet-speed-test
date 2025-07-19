# app.py
import streamlit as st
import speedtest
import time

# Set up page config
st.set_page_config(page_title="Internet Speed Checker", layout="centered")

# Custom CSS styling
st.markdown("""
    <style>
        body {
            background-color: #ffffff;  /* White page background */
            color: #000000;             /* Black text */
        }

        .main {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            border: 2px solid #2196f3;  /* Blue border */
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 900px;
            margin: auto;
        }

        .status {
            font-size: 24px;
            margin-top: 20px;
            padding: 10px;
            border-radius: 5px;
        }

        .online {
            background-color: #4caf50;
            color: white;
        }

        .offline {
            background-color: #f44336;
            color: white;
        }

        .stButton {
            display: flex;
            justify-content: center;
            margin-top: 25px;
        }

        .stButton>button {
            background-color: #2196f3;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            border: none;
        }

        .stButton>button:hover {
            background-color: #1976d2;
        }

        .metrics {
            font-size: 18px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Main title box
st.markdown('<div class="main"><h1>Internet Speed Checker</h1>', unsafe_allow_html=True)

# Speed check logic
if st.button("Check Speed"):
    st.write("Running speed test... Please wait ⏳")
    try:
        wifi = speedtest.Speedtest()
        wifi.get_best_server()  # Ensure accurate server
        time.sleep(1)  # Small delay to stabilize

        # Perform test
        download_bps = wifi.download()
        upload_bps = wifi.upload()
        ping = wifi.results.ping

        # Convert to Mbps and MB/s
        download_mbps = round(download_bps / 1_000_000, 2)
        upload_mbps = round(upload_bps / 1_000_000, 2)
        download_mbs = round(download_mbps / 8, 2)  # MB/s
        upload_mbs = round(upload_mbps / 8, 2)

        st.markdown(f'<p class="status online">Status: Online</p>', unsafe_allow_html=True)
        st.success(f"📥 Download Speed: {download_mbps} Mbps ({download_mbs} MB/s)")
        st.success(f"📤 Upload Speed: {upload_mbps} Mbps ({upload_mbs} MB/s)")
        st.info(f"🕒 Ping: {ping} ms")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.markdown(f'<p class="status offline">Status: Unknown (Click button)</p>', unsafe_allow_html=True)

# Close box
st.markdown('</div>', unsafe_allow_html=True)
