"""
log_parser.py
-------------
Core MAVLink log file parser.
Supports .tlog (telemetry logs) and .bin (ArduPilot DataFlash) formats.
"""

import io
from pathlib import Path

import pandas as pd
import numpy as np
from loguru import logger


class LogParser:
    """
    Parses MAVLink .tlog and ArduPilot .bin log files into a
    normalized pandas DataFrame for downstream analysis and visualization.
    """

    # MAVLink message types we care about
    MESSAGES_OF_INTEREST = {
        "GLOBAL_POSITION_INT",
        "ATTITUDE",
        "VFR_HUD",
        "SYS_STATUS",
        "GPS_RAW_INT",
        "HEARTBEAT",
    }

    def parse_file(self, filepath: Path) -> pd.DataFrame:
        """Parse a log file from a filesystem path."""
        filepath = Path(filepath)
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return pd.DataFrame()

        suffix = filepath.suffix.lower()
        logger.info(f"Parsing {suffix} log: {filepath.name}")

        if suffix == ".tlog":
            return self._parse_tlog(str(filepath))
        elif suffix in (".bin", ".log"):
            return self._parse_bin(str(filepath))
        else:
            logger.warning(f"Unsupported file format: {suffix}")
            return pd.DataFrame()

    def parse_uploaded_file(self, uploaded_file) -> pd.DataFrame:
        """Parse a Streamlit UploadedFile object."""
        suffix = Path(uploaded_file.name).suffix.lower()
        logger.info(f"Parsing uploaded file: {uploaded_file.name}")

        # Write to a temp file so pymavlink can read it
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            df = self.parse_file(Path(tmp_path))
        finally:
            os.unlink(tmp_path)

        return df

    # ── Private parsers ───────────────────────────────────────────────────────

    def _parse_tlog(self, filepath: str) -> pd.DataFrame:
        """Parse a MAVLink .tlog telemetry log using pymavlink."""
        try:
            from pymavlink import mavutil
        except ImportError:
            logger.error("pymavlink not installed. Run: pip install pymavlink")
            return pd.DataFrame()

        records = []
        try:
            mlog = mavutil.mavlink_connection(filepath, dialect="ardupilotmega")
            while True:
                msg = mlog.recv_match(
                    type=list(self.MESSAGES_OF_INTEREST), blocking=False
                )
                if msg is None:
                    break
                record = self._extract_fields(msg)
                if record:
                    records.append(record)
        except Exception as e:
            logger.error(f"Error parsing .tlog: {e}")
            return pd.DataFrame()

        return self._build_dataframe(records)

    def _parse_bin(self, filepath: str) -> pd.DataFrame:
        """Parse an ArduPilot DataFlash .bin log using pymavlink."""
        try:
            from pymavlink import mavutil, DFReader
        except ImportError:
            logger.error("pymavlink not installed. Run: pip install pymavlink")
            return pd.DataFrame()

        records = []
        try:
            mlog = mavutil.mavlink_connection(filepath, dialect="ardupilotmega")
            while True:
                msg = mlog.recv_match(blocking=False)
                if msg is None:
                    break
                if msg.get_type() in self.MESSAGES_OF_INTEREST:
                    record = self._extract_fields(msg)
                    if record:
                        records.append(record)
        except Exception as e:
            logger.error(f"Error parsing .bin: {e}")
            return pd.DataFrame()

        return self._build_dataframe(records)

    def _extract_fields(self, msg) -> dict | None:
        """Extract normalized fields from a MAVLink message."""
        msg_type = msg.get_type()
        timestamp = getattr(msg, "_timestamp", None)
        record = {"msg_type": msg_type, "timestamp": timestamp}

        try:
            if msg_type == "GLOBAL_POSITION_INT":
                record.update({
                    "lat": msg.lat / 1e7,
                    "lon": msg.lon / 1e7,
                    "altitude": msg.relative_alt / 1000.0,  # mm → m
                    "altitude_msl": msg.alt / 1000.0,
                })
            elif msg_type == "ATTITUDE":
                record.update({
                    "roll": np.degrees(msg.roll),
                    "pitch": np.degrees(msg.pitch),
                    "yaw": np.degrees(msg.yaw),
                    "rollspeed": np.degrees(msg.rollspeed),
                    "pitchspeed": np.degrees(msg.pitchspeed),
                    "yawspeed": np.degrees(msg.yawspeed),
                })
            elif msg_type == "VFR_HUD":
                record.update({
                    "airspeed": msg.airspeed,
                    "groundspeed": msg.groundspeed,
                    "heading": msg.heading,
                    "throttle": msg.throttle,
                    "climb_rate": msg.climb,
                })
            elif msg_type == "SYS_STATUS":
                record.update({
                    "battery_voltage": msg.voltage_battery / 1000.0,  # mV → V
                    "battery_current": msg.current_battery / 100.0,   # cA → A
                    "battery_remaining": msg.battery_remaining,
                })
            elif msg_type == "GPS_RAW_INT":
                record.update({
                    "gps_fix_type": msg.fix_type,
                    "gps_satellites": msg.satellites_visible,
                    "gps_hdop": msg.eph / 100.0,
                })
            elif msg_type == "HEARTBEAT":
                record.update({
                    "base_mode": msg.base_mode,
                    "system_status": msg.system_status,
                })
            else:
                return None
        except AttributeError as e:
            logger.debug(f"Missing field in {msg_type}: {e}")
            return None

        return record

    def _build_dataframe(self, records: list) -> pd.DataFrame:
        """Convert raw record list into a clean, merged DataFrame."""
        if not records:
            logger.warning("No records parsed from log file.")
            return pd.DataFrame()

        df = pd.DataFrame(records)

        # Sort by timestamp
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp").reset_index(drop=True)

        # Forward-fill across message types to align all fields on one timeline
        df = df.ffill()

        logger.info(f"Parsed {len(df)} records across {df['msg_type'].nunique()} message types")
        return df
