"""
charts.py
---------
Plotly chart builders for MAVLink telemetry data.
Each function accepts a normalized DataFrame and returns a Plotly Figure.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def plot_altitude(df: pd.DataFrame) -> go.Figure:
    """Plot altitude over time with a clean filled area chart."""
    fig = go.Figure()

    if "altitude" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["altitude"],
            name="Relative Altitude (m)",
            line=dict(color="#00BFFF", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 191, 255, 0.15)",
        ))

    if "altitude_msl" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["altitude_msl"],
            name="Altitude MSL (m)",
            line=dict(color="#FF8C00", width=1.5, dash="dot"),
        ))

    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Altitude (m)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=20, t=20, b=40),
        hovermode="x unified",
    )
    return fig


def plot_attitude(df: pd.DataFrame) -> go.Figure:
    """Plot roll, pitch, and yaw over time on a shared axis."""
    fig = go.Figure()

    colors = {"roll": "#FF4B4B", "pitch": "#00CC88", "yaw": "#7B68EE"}

    for channel in ["roll", "pitch", "yaw"]:
        if channel in df.columns:
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df[channel],
                name=channel.capitalize() + " (°)",
                line=dict(color=colors[channel], width=1.8),
            ))

    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title="Angle (degrees)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=20, t=20, b=40),
        hovermode="x unified",
    )
    return fig


def plot_battery(df: pd.DataFrame) -> go.Figure:
    """Plot battery voltage and remaining % as a dual-axis chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if "battery_voltage" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["battery_voltage"],
                name="Voltage (V)",
                line=dict(color="#FFD700", width=2),
            ),
            secondary_y=False,
        )

    if "battery_remaining" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["battery_remaining"],
                name="Remaining (%)",
                line=dict(color="#32CD32", width=1.5, dash="dot"),
            ),
            secondary_y=True,
        )

    fig.update_xaxes(title_text="Time (s)")
    fig.update_yaxes(title_text="Voltage (V)", secondary_y=False)
    fig.update_yaxes(title_text="Remaining (%)", secondary_y=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=40, r=40, t=20, b=40),
        hovermode="x unified",
    )
    return fig


def plot_gps_overview(df: pd.DataFrame) -> go.Figure:
    """Quick 2D lat/lon scatter plot as a lightweight GPS overview."""
    if not all(c in df.columns for c in ["lat", "lon"]):
        return go.Figure()

    gps_df = df[["lat", "lon"]].dropna()

    fig = px.scatter(
        gps_df,
        x="lon",
        y="lat",
        color_discrete_sequence=["#00BFFF"],
        labels={"lon": "Longitude", "lat": "Latitude"},
    )

    # Mark start and end
    fig.add_trace(go.Scatter(
        x=[gps_df["lon"].iloc[0]],
        y=[gps_df["lat"].iloc[0]],
        mode="markers",
        marker=dict(size=12, color="green", symbol="circle"),
        name="Start",
    ))
    fig.add_trace(go.Scatter(
        x=[gps_df["lon"].iloc[-1]],
        y=[gps_df["lat"].iloc[-1]],
        mode="markers",
        marker=dict(size=12, color="red", symbol="x"),
        name="End",
    ))

    fig.update_layout(
        xaxis_title="Longitude",
        yaxis_title="Latitude",
        margin=dict(l=40, r=20, t=20, b=40),
    )
    return fig


def plot_anomalies_overlay(df: pd.DataFrame, anomalies: pd.DataFrame, channel: str) -> go.Figure:
    """Overlay detected anomaly points on top of a telemetry channel."""
    fig = go.Figure()

    if channel in df.columns:
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df[channel],
            name=channel,
            line=dict(color="#888888", width=1.5),
        ))

    if not anomalies.empty and channel in anomalies.columns:
        anom = anomalies[anomalies["channel"] == channel] if "channel" in anomalies.columns else anomalies
        fig.add_trace(go.Scatter(
            x=anom["timestamp"],
            y=anom[channel],
            mode="markers",
            marker=dict(color="red", size=8, symbol="x"),
            name="Anomaly",
        ))

    fig.update_layout(
        xaxis_title="Time (s)",
        yaxis_title=channel,
        margin=dict(l=40, r=20, t=20, b=40),
        hovermode="x unified",
    )
    return fig
