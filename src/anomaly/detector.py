"""
test_parser.py
--------------
Unit tests for the LogParser.
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.parser.log_parser import LogParser


class TestLogParser:

    def test_parse_nonexistent_file_returns_empty(self):
        parser = LogParser()
        result = parser.parse_file(Path("nonexistent_file.tlog"))
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_unsupported_format_returns_empty(self, tmp_path):
        dummy = tmp_path / "test.csv"
        dummy.write_text("col1,col2\n1,2\n")
        parser = LogParser()
        result = parser.parse_file(dummy)
        assert result.empty

    def test_build_dataframe_from_records(self):
        parser = LogParser()
        records = [
            {"msg_type": "GLOBAL_POSITION_INT", "timestamp": 1.0, "lat": 37.77, "lon": -122.41, "altitude": 10.0},
            {"msg_type": "ATTITUDE", "timestamp": 1.1, "roll": 0.5, "pitch": -0.2, "yaw": 90.0},
            {"msg_type": "SYS_STATUS", "timestamp": 1.2, "battery_voltage": 12.4, "battery_remaining": 85},
        ]
        df = parser._build_dataframe(records)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert "timestamp" in df.columns

    def test_build_dataframe_empty_records(self):
        parser = LogParser()
        df = parser._build_dataframe([])
        assert df.empty

    def test_dataframe_sorted_by_timestamp(self):
        parser = LogParser()
        records = [
            {"msg_type": "ATTITUDE", "timestamp": 3.0, "roll": 1.0},
            {"msg_type": "ATTITUDE", "timestamp": 1.0, "roll": 2.0},
            {"msg_type": "ATTITUDE", "timestamp": 2.0, "roll": 3.0},
        ]
        df = parser._build_dataframe(records)
        timestamps = df["timestamp"].tolist()
        assert timestamps == sorted(timestamps)
