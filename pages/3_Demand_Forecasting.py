
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Demand Forecasting",
    page_icon="📈",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "forecast_results.csv"


@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


forecast = load_data()

forecast["ds"] = pd.to_datetime(forecast["ds"])

st.title("📈 Demand Forecasting")
st.caption("30-Day Sales Forecast using Facebook Prophet")

# -----------------------------
# KPI Cards
# -----------------------------

latest_prediction = forecast.iloc[-1]["yhat"]
highest_prediction = forecast["yhat"].max()
lowest_prediction = forecast["yhat"].min()
average_prediction = forecast["yhat"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Latest Forecast", f"£{latest_prediction:,.0f}")
c2.metric("Highest Forecast", f"£{highest_prediction:,.0f}")
c3.metric("Lowest Forecast", f"£{lowest_prediction:,.0f}")
c4.metric("Average Forecast", f"£{average_prediction:,.0f}")

st.divider()

# -----------------------------
# Forecast Line
# -----------------------------

fig = px.line(
    forecast,
    x="ds",
    y="yhat",
    title="Sales Forecast",
    labels={
        "ds":"Date",
        "yhat":"Predicted Revenue (£)"
    }
)

fig.update_traces(line_width=3)

st.plotly_chart(
    fig,
    use_container_width=True
)

# -----------------------------
# Forecast Confidence Interval
# -----------------------------

fig2 = px.line(
    forecast,
    x="ds",
    y=["yhat","yhat_upper","yhat_lower"],
    title="Forecast Confidence Interval"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# -----------------------------
# Forecast Table
# -----------------------------

st.subheader("Forecast Data")

table = forecast[
    ["ds","yhat","yhat_lower","yhat_upper"]
].copy()

table.columns=[
    "Date",
    "Predicted Revenue",
    "Lower Bound",
    "Upper Bound"
]

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Download Button
# -----------------------------

csv = table.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Forecast",
    csv,
    "forecast_report.csv",
    "text/csv"
)

st.success("Demand Forecasting Completed Successfully.")
