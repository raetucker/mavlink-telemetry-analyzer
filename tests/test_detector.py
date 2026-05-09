"""
test_detector.py
----------------
Unit tests for the AnomalyDetector.
"""

import numpy as np
import pandas as pd

from src.anomaly.detector import AnomalyDetector


@pytest.fixture
def clean_df():
    """A clean telemetry DataFrame with no anomalies."""
    n = 200
    return pd.DataFrame({
        "timestamp": np.linspace(0, 100, n),
        "altitude": np.sin(np.linspace(0, 2 * np.pi, n)) * 10 + 50,
        "battery_voltage": np.linspace(12.6, 11.0, n),
        "roll": np.random.normal(0, 2, n),
        "pitch": np.random.normal(0, 2, n),
        "yaw": np.linspace(0, 180, n),
    })


@pytest.fixture
def anomalous_df(clean_df):
    """A DataFrame with injected anomalies at known indices."""
    df = clean_df.copy()
    df.loc[50, "altitude"] = 999.0    # Obvious altitude spike
    df.loc[100, "battery_voltage"] = 0.1  # Obvious battery drop
    return df


class TestAnomalyDetector:

    def test_no_anomalies_on_clean_data(self, clean_df):
        detector = AnomalyDetector(zscore_threshold=3.0, rolling_window=20)
        anomalies = detector.detect(clean_df)
        assert anomalies.empty or len(anomalies) < 5  # Allow minor noise flags

    def test_detects_altitude_spike(self, anomalous_df):
        detector = AnomalyDetector(zscore_threshold=3.0, rolling_window=20)
        anomalies = detector.detect(anomalous_df)
        assert not anomalies.empty
        altitude_anomalies = anomalies[anomalies["channel"] == "altitude"]
        assert len(altitude_anomalies) > 0

    def test_detects_battery_drop(self, anomalous_df):
        detector = AnomalyDetector(zscore_threshold=3.0, rolling_window=20)
        anomalies = detector.detect(anomalous_df)
        battery_anomalies = anomalies[anomalies["channel"] == "battery_voltage"]
        assert len(battery_anomalies) > 0

    def test_higher_threshold_fewer_anomalies(self, anomalous_df):
        low_detector = AnomalyDetector(zscore_threshold=2.0)
        high_detector = AnomalyDetector(zscore_threshold=5.0)
        low_anom = low_detector.detect(anomalous_df)
        high_anom = high_detector.detect(anomalous_df)
        assert len(low_anom) >= len(high_anom)

    def test_empty_dataframe_returns_empty(self):
        detector = AnomalyDetector()
        result = detector.detect(pd.DataFrame())
        assert result.empty

    def test_anomaly_report_has_required_columns(self, anomalous_df):
        detector = AnomalyDetector(zscore_threshold=2.0)
        anomalies = detector.detect(anomalous_df)
        if not anomalies.empty:
            assert "timestamp" in anomalies.columns
            assert "channel" in anomalies.columns
            assert "method" in anomalies.columns
            assert "score" in anomalies.columns
