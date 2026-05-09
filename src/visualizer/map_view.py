"""
map_view.py
-----------
Renders an interactive GPS flight path map using Folium.
Returns an HTML string for embedding in Streamlit via st.components.v1.html()
"""

import pandas as pd
import folium


def render_flight_map(df: pd.DataFrame) -> str:
    """
    Render an interactive Folium map of the GPS flight path.

    Args:
        df: Normalized telemetry DataFrame with 'lat' and 'lon' columns

    Returns:
        HTML string of the rendered map
    """
    gps_df = df[["lat", "lon"]].dropna()
    gps_df = gps_df[
        (gps_df["lat"] != 0) & (gps_df["lon"] != 0)
    ]

    if gps_df.empty:
        return "<p>No valid GPS data available.</p>"

    # Center map on mean position
    center_lat = gps_df["lat"].mean()
    center_lon = gps_df["lon"].mean()

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=16,
        tiles="CartoDB positron",
    )

    # Draw flight path
    coordinates = list(zip(gps_df["lat"], gps_df["lon"]))
    folium.PolyLine(
        coordinates,
        color="#00BFFF",
        weight=3,
        opacity=0.85,
        tooltip="Flight Path",
    ).add_to(m)

    # Start marker
    folium.Marker(
        location=coordinates[0],
        popup="🟢 Takeoff",
        icon=folium.Icon(color="green", icon="plane", prefix="fa"),
    ).add_to(m)

    # End marker
    folium.Marker(
        location=coordinates[-1],
        popup="🔴 Landing",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)

    return m._repr_html_()
