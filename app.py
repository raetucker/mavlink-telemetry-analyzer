"""
MAVLink Telemetry Analyzer
--------------------------
Main Streamlit dashboard entry point.
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from src.parser.log_parser import LogParser
from src.visualizer.charts import (
    plot_altitude,
    plot_attitude,
    plot_battery,
    plot_gps_overview,
)
from src.anomaly.detector import AnomalyDetector

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MAVLink Telemetry Analyzer",
    page_icon="🛸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛸 MAVLink Analyzer")
    st.markdown("---")

    st.subheader("📂 Log File")
    upload_mode = st.radio(
        "Data source",
        ["Upload a log file", "Use sample log"],
        index=1,
    )

    uploaded_file = None
    if upload_mode == "Upload a log file":
        uploaded_file = st.file_uploader(
            "Upload MAVLink log (.tlog or .bin)",
            type=["tlog", "bin", "log"],
        )
    else:
        sample_dir = Path("data/sample_logs")
        sample_files = list(sample_dir.glob("*.tlog")) + list(sample_dir.glob("*.bin"))
        if sample_files:
            selected_sample = st.selectbox(
                "Select sample log",
                [f.name for f in sample_files],
            )
        else:
            st.warning("No sample logs found in data/sample_logs/")
            st.info("Add .tlog or .bin files to data/sample_logs/ to use this mode.")
            selected_sample = None

    st.markdown("---")
    st.subheader("⚙️ Anomaly Detection")
    zscore_threshold = st.slider(
        "Z-Score threshold", min_value=1.0, max_value=5.0, value=3.0, step=0.5
    )
    rolling_window = st.slider(
        "Rolling window (samples)", min_value=5, max_value=100, value=20, step=5
    )

    st.markdown("---")
    st.caption("github.com/raetucker/mavlink-telemetry-analyzer")

# ── Main Dashboard ────────────────────────────────────────────────────────────
st.title("🛸 MAVLink Telemetry Analyzer")
st.markdown(
    "_A real-time MAVLink flight log parser, visualizer, and anomaly detector "
    "for ArduPilot/PX4 UAV systems_"
)
st.markdown("---")

# ── Load data ─────────────────────────────────────────────────────────────────
parser = LogParser()
df = None

if upload_mode == "Upload a log file" and uploaded_file is not None:
    with st.spinner("Parsing log file..."):
        df = parser.parse_uploaded_file(uploaded_file)
elif upload_mode == "Use sample log" and selected_sample:
    with st.spinner("Loading sample log..."):
        df = parser.parse_file(Path("data/sample_logs") / selected_sample)

# ── No data state ─────────────────────────────────────────────────────────────
if df is None or df.empty:
    st.info(
        "👈 Upload a MAVLink log file or select a sample log from the sidebar to get started."
    )
    st.markdown("### Supported formats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**`.tlog`** — MAVLink telemetry log (GCS recorded)")
    with col2:
        st.markdown("**`.bin`** — ArduPilot DataFlash binary log")
    with col3:
        st.markdown("**`.log`** — ArduPilot text log")
    st.stop()

# ── Data loaded — show summary ────────────────────────────────────────────────
st.success(f"✅ Log parsed — {len(df):,} telemetry records loaded")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Records", f"{len(df):,}")
with col2:
    duration = df["timestamp"].max() - df["timestamp"].min() if "timestamp" in df.columns else 0
    st.metric("Flight Duration", f"{duration:.1f}s" if duration else "N/A")
with col3:
    max_alt = df["altitude"].max() if "altitude" in df.columns else None
    st.metric("Max Altitude", f"{max_alt:.1f}m" if max_alt else "N/A")
with col4:
    min_batt = df["battery_voltage"].min() if "battery_voltage" in df.columns else None
    st.metric("Min Battery", f"{min_batt:.2f}V" if min_batt else "N/A")

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Telemetry", "🗺️ GPS Track", "🚨 Anomalies", "📋 Raw Data", "ℹ️ About"]
)

# ── Tab 1: Telemetry Charts ───────────────────────────────────────────────────
with tab1:
    st.subheader("Altitude")
    if "altitude" in df.columns:
        st.plotly_chart(plot_altitude(df), use_container_width=True)
    else:
        st.warning("No altitude data found in this log.")

    st.subheader("Attitude (Roll / Pitch / Yaw)")
    if all(c in df.columns for c in ["roll", "pitch", "yaw"]):
        st.plotly_chart(plot_attitude(df), use_container_width=True)
    else:
        st.warning("No attitude data found in this log.")

    st.subheader("Battery Voltage")
    if "battery_voltage" in df.columns:
        st.plotly_chart(plot_battery(df), use_container_width=True)
    else:
        st.warning("No battery data found in this log.")

# ── Tab 2: GPS Map ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("GPS Flight Path")
    if all(c in df.columns for c in ["lat", "lon"]):
        from src.visualizer.map_view import render_flight_map
        st.components.v1.html(render_flight_map(df), height=500)
    else:
        st.warning("No GPS data found in this log.")

# ── Tab 3: Anomaly Detection ──────────────────────────────────────────────────
with tab3:
    st.subheader("🚨 Anomaly Detection Results")
    detector = AnomalyDetector(
        zscore_threshold=zscore_threshold,
        rolling_window=rolling_window,
    )
    anomalies = detector.detect(df)

    if anomalies.empty:
        st.success("✅ No anomalies detected with current settings.")
    else:
        st.error(f"⚠️ {len(anomalies)} anomalous readings detected")
        st.dataframe(anomalies, use_container_width=True)
        csv = anomalies.to_csv(index=False)
        st.download_button(
            "📥 Download anomaly report (CSV)",
            data=csv,
            file_name="anomaly_report.csv",
            mime="text/csv",
        )

# ── Tab 4: Raw Data ───────────────────────────────────────────────────────────
with tab4:
    st.subheader("Raw Telemetry Data")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download parsed data (CSV)",
        data=csv,
        file_name="telemetry_parsed.csv",
        mime="text/csv",
    )

# ── Tab 5: About ──────────────────────────────────────────────────────────────
with tab5:
    st.markdown("""
    ## About MAVLink Telemetry Analyzer

    This tool parses, visualizes, and analyzes MAVLink flight logs from
    ArduPilot and PX4 autopilot systems.

    **Supported MAVLink messages:**
    - `GLOBAL_POSITION_INT` — GPS latitude, longitude, altitude
    - `ATTITUDE` — Roll, pitch, yaw
    - `VFR_HUD` — Airspeed, groundspeed, heading, throttle
    - `SYS_STATUS` — Battery voltage, current, remaining %
    - `GPS_RAW_INT` — Raw GPS fix and satellite count
    - `HEARTBEAT` — System mode and health

    **Anomaly Detection Methods:**
    - Z-Score thresholding (active)
    - Rolling mean ± std deviation (active)
    - Isolation Forest (coming soon)
    - Autoencoder reconstruction error (planned)

    **Links:**
    - [GitHub Repository](https://github.com/raetucker/mavlink-telemetry-analyzer)
    - [MAVLink Protocol](https://mavlink.io/en/)
    - [ArduPilot](https://ardupilot.org/)
    - [PX4](https://px4.io/)
    """)
