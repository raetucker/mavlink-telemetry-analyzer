"""
detector.py
-----------
Anomaly detection engine for MAVLink telemetry data.
"""

import pandas as pd
import numpy as np
from loguru import logger

MONITORED_CHANNELS = [
    "altitude", "roll", "pitch", "yaw",
    "battery_voltage", "airspeed", "groundspeed", "climb_rate",
]

class AnomalyDetector:
    def __init__(self, zscore_threshold: float = 3.0, rolling_window: int = 20):
        self.zscore_threshold = zscore_threshold
        self.rolling_window = rolling_window

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()
        all_anomalies = []
        for channel in MONITORED_CHANNELS:
            if channel not in df.columns:
                continue
            series = df[channel].dropna()
            if len(series) < self.rolling_window:
                continue
            zscore_anom = self._zscore_detection(df, channel)
            if not zscore_anom.empty:
                all_anomalies.append(zscore_anom)
            rolling_anom = self._rolling_detection(df, channel)
            if not rolling_anom.empty:
                all_anomalies.append(rolling_anom)
        if not all_anomalies:
            return pd.DataFrame()
        combined = pd.concat(all_anomalies, ignore_index=True)
        combined = combined.drop_duplicates(subset=["timestamp", "channel"])
        return combined.sort_values("timestamp").reset_index(drop=True)

    def _zscore_detection(self, df, channel):
        series = df[channel].dropna()
        mean, std = series.mean(), series.std()
        if std == 0:
            return pd.DataFrame()
        zscores = (df[channel] - mean) / std
        mask = zscores.abs() > self.zscore_threshold
        anomalies = df[mask].copy()
        anomalies["channel"] = channel
        anomalies["method"] = "z-score"
        anomalies["score"] = zscores[mask].abs().round(3)
        return anomalies[["timestamp", "channel", channel, "method", "score"]]

    def _rolling_detection(self, df, channel):
        series = df[channel]
        rolling_mean = series.rolling(window=self.rolling_window, center=True).mean()
        rolling_std = series.rolling(window=self.rolling_window, center=True).std()
        deviation = (series - rolling_mean).abs()
        threshold = self.zscore_threshold * rolling_std
        mask = (deviation > threshold).fillna(False)
        anomalies = df[mask].copy()
        anomalies["channel"] = channel
        anomalies["method"] = "rolling-stats"
        anomalies["score"] = (deviation[mask] / rolling_std[mask]).round(3)
        return anomalies[["timestamp", "channel", channel, "method", "score"]]
