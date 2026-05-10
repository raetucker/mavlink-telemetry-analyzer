# MAVLink Telemetry Analyzer

A real-time MAVLink flight log parser, visualizer, and anomaly detector for ArduPilot/PX4 UAV systems

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active%20Development-orange)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

---

# Overview

**MAVLink Telemetry Analyzer** is an open-source tool for ingesting, parsing, visualizing, and analyzing flight telemetry logs from MAVLink-based UAV systems including **ArduPilot** and **PX4**. It provides an interactive Streamlit dashboard for exploring flight data and a growing anomaly detection engine for identifying irregular flight behavior.

Whether you're a researcher, developer, or hobbyist working with autonomous systems, this tool makes it easy to understand what happened during a flight — and flag anything that shouldn't have.

---

# Features

- **Log Ingestion** — Parse `.tlog`, `.bin`, and `.log` files from ArduPilot/PX4 flight controllers
- **Interactive Dashboard** — Visualize altitude, GPS track, battery voltage, airspeed, attitude (roll/pitch/yaw), and more
- **GPS Path Mapping** — Plot flight paths on an interactive map
- **Anomaly Detection** — Z-score and rolling statistics-based detection of irregular sensor readings
- **Time-Series Analysis** — Zoom, filter, and compare telemetry channels across a flight
- **Extensible Architecture** — Modular design makes it easy to add new message types, detectors, and visualizations
- **Sample Data Included** — Public ArduPilot logs included for immediate testing

---

# Project Structure

```
mavlink-telemetry-analyzer/
├── src/
│   ├── parser/             # MAVLink log parsing and message extraction
│   │   ├── __init__.py
│   │   ├── log_parser.py   # Core parser for .tlog/.bin files
│   │   └── message_types.py# MAVLink message type definitions
│   ├── visualizer/         # Chart and map rendering
│   │   ├── __init__.py
│   │   ├── charts.py       # Time-series and telemetry charts
│   │   └── map_view.py     # GPS path visualization
│   └── anomaly/            # Anomaly detection engine
│       ├── __init__.py
│       └── detector.py     # Z-score and rolling stat detectors
├── data/
│   └── sample_logs/        # Public ArduPilot/PX4 sample log files
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation and architecture notes
├── app.py                  # Streamlit dashboard entry point
├── requirements.txt        # Python dependencies
├── .gitignore
└── README.md
```

---

# Getting Started

# Prerequisites

- Python 3.10+
- pip

# Installation

```bash
# Clone the repository
git clone https://github.com/raetucker/mavlink-telemetry-analyzer.git
cd mavlink-telemetry-analyzer

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

# Running the Dashboard

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

---

# Usage

1. Launch the dashboard with `streamlit run app.py`
2. Upload a MAVLink `.tlog` or `.bin` log file — or use a provided sample log
3. Select telemetry channels to visualize (altitude, battery, GPS, attitude, etc.)
4. Review the anomaly detection panel for flagged events
5. Export flagged anomalies or charts as needed

---

# Anomaly Detection

The anomaly engine currently supports:

| Method | Description | Status |
|---|---|---|
| Z-Score | Flags readings beyond N standard deviations | Implemented |
| Rolling Mean ± Std | Detects drift from a rolling baseline | Implemented |
| Isolation Forest | ML-based multivariate anomaly detection | In Progress |
| Autoencoder | Deep learning reconstruction-error detection | Planned |

---

# Roadmap

- [x] Project scaffold and architecture
- [ ] Core MAVLink `.tlog` parser
- [ ] MAVLink `.bin` (DataFlash) parser
- [ ] Streamlit dashboard — telemetry time-series charts
- [ ] GPS path map view
- [ ] Z-score anomaly detector
- [ ] Rolling statistics anomaly detector
- [ ] Anomaly event timeline overlay
- [ ] Isolation Forest detector
- [ ] Multi-log comparison view
- [ ] Autoencoder-based anomaly detection
- [ ] Export anomaly reports as PDF/CSV
- [ ] CLI interface for headless use
- [ ] Docker support

---

# Running Tests

```bash
pytest tests/
```

---

# Supported MAVLink Message Types

| Message | Description |
|---|---|
| `GLOBAL_POSITION_INT` | GPS latitude, longitude, altitude |
| `ATTITUDE` | Roll, pitch, yaw angles |
| `VFR_HUD` | Airspeed, groundspeed, heading, throttle |
| `SYS_STATUS` | Battery voltage, current, remaining % |
| `GPS_RAW_INT` | Raw GPS fix data and satellite count |
| `HEARTBEAT` | System mode and status |

More message types added continuously.

---

# Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change. See the [contribution guidelines](docs/CONTRIBUTING.md) for more detail.

---

# License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

# Acknowledgements

- [MAVLink Protocol](https://mavlink.io/en/) — the lightweight messaging protocol for UAVs
- [ArduPilot](https://ardupilot.org/) — open-source autopilot system
- [PX4](https://px4.io/) — open-source flight control software
- [pymavlink](https://github.com/ArduPilot/pymavlink) — Python MAVLink library
