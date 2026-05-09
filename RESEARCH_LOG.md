# Research & Development Log

A running log of daily progress, decisions, findings, and next steps.
Each entry is a natural commit — no code required.

---

## 2026-05-09 — Project Initialized

**What was done:**
- Initialized project repository `mavlink-telemetry-analyzer`
- Defined project scope: MAVLink `.tlog` and `.bin` parser, Streamlit dashboard, statistical anomaly detection
- Scaffolded full project structure: `src/parser`, `src/visualizer`, `src/anomaly`, `tests/`, `data/`
- Wrote core modules: `log_parser.py`, `charts.py`, `map_view.py`, `detector.py`
- Wrote initial unit tests for parser and anomaly detector
- Set up `requirements.txt` with pinned dependencies

**Decisions made:**
- Chose `pymavlink` as the primary parsing library — it's the official Python MAVLink library maintained by the ArduPilot team, supports both `.tlog` and `.bin` formats
- Chose Streamlit for the dashboard — fast to iterate, visually strong for portfolio, well-regarded in the ML/data science community
- Started anomaly detection with Z-Score and rolling statistics before moving to ML methods — establishes a statistical baseline to compare against later
- Used `loguru` for logging instead of the stdlib `logging` — cleaner API and better output formatting
- Forward-fill strategy for aligning multi-message-type telemetry into a single DataFrame

**Technical notes:**
- MAVLink `GLOBAL_POSITION_INT` encodes lat/lon as integers × 1e7 — must divide to get decimal degrees
- Altitude in `GLOBAL_POSITION_INT` is in millimeters — divide by 1000 for meters
- Battery voltage in `SYS_STATUS` is in millivolts — divide by 1000 for volts
- Attitude angles from MAVLink are in radians — convert with `np.degrees()` for display

**Next steps:**
- [ ] Download public ArduPilot sample logs and add to `data/sample_logs/`
- [ ] Test parser against real `.tlog` files
- [ ] Verify Streamlit dashboard renders correctly end-to-end
- [ ] Add message_types.py constants file
- [ ] Add GitHub Actions CI workflow for running pytest on push

---

_Add new entries at the top in reverse chronological order._
