# app.py
import streamlit as st
import speedtest

st.set_page_config(page_title="Internet Speed Checker", layout="centered")

st.title("⚡ Internet Speed Checker")

if st.button("Check Speed"):
    st.write("Running speed test... Please wait ⏳")
    try:
        wifi = speedtest.Speedtest()
        wifi.get_best_server()

        # Run download and upload tests
        download_bps = wifi.download()
        upload_bps = wifi.upload()
        ping = wifi.results.ping

        # Convert to Mbps (bits per second to megabits per second)
        download_mbps = round(download_bps / 1_000_000, 2)
        upload_mbps = round(upload_bps / 1_000_000, 2)

        st.success(f"📥 **Download Speed:** {download_mbps} Mbps")
        st.success(f"📤 **Upload Speed:** {upload_mbps} Mbps")
        st.info(f"🕒 **Ping:** {ping} ms")

    except Exception as e:
        st.error(f"Error: {e}")
