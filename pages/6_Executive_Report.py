
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Executive Report",
    page_icon="📄",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent

SALES_PATH = BASE_DIR / "data" / "online_retail.csv"
SEGMENTS_PATH = BASE_DIR / "data" / "customer_segments.csv"
CHURN_PATH = BASE_DIR / "data" / "customer_churn.csv"
INVENTORY_PATH = BASE_DIR / "data" / "inventory_summary.csv"
FORECAST_PATH = BASE_DIR / "data" / "forecast_results.csv"


@st.cache_data
def load_data():
    sales = pd.read_csv(SALES_PATH)
    segments = pd.read_csv(SEGMENTS_PATH)
    churn = pd.read_csv(CHURN_PATH)
    inventory = pd.read_csv(INVENTORY_PATH)
    forecast = pd.read_csv(FORECAST_PATH)

    sales["InvoiceDate"] = pd.to_datetime(
        sales["InvoiceDate"],
        errors="coerce"
    )

    if "Revenue" not in sales.columns:
        sales["Revenue"] = sales["Quantity"] * sales["Price"]

    forecast["ds"] = pd.to_datetime(
        forecast["ds"],
        errors="coerce"
    )

    unnamed_columns = [
        column
        for column in segments.columns
        if column.lower().startswith("unnamed")
    ]

    if unnamed_columns:
        segments = segments.rename(
            columns={unnamed_columns[0]: "CustomerID"}
        )

    return sales, segments, churn, inventory, forecast


try:
    sales, segments, churn, inventory, forecast = load_data()
except Exception as error:
    st.error(f"Unable to load report data: {error}")
    st.stop()


st.title("📄 Executive Report")
st.caption(
    "Consolidated business findings from sales, customer, forecasting, "
    "churn and inventory analytics."
)

# -----------------------------
# Executive KPIs
# -----------------------------
total_revenue = sales["Revenue"].sum()
total_orders = sales["Invoice"].nunique()
total_customers = sales["Customer ID"].nunique()
total_products = sales["StockCode"].nunique()

churn_rate = (
    churn["Churn"].mean() * 100
    if "Churn" in churn.columns
    else 0
)

forecast_average = (
    forecast["yhat"].tail(30).mean()
    if "yhat" in forecast.columns
    else 0
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Revenue",
    f"£{total_revenue:,.0f}"
)

c2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

c3.metric(
    "Customers",
    f"{total_customers:,}"
)

c4.metric(
    "Churn Rate",
    f"{churn_rate:.2f}%"
)

st.divider()

# -----------------------------
# Project overview
# -----------------------------
st.subheader("Project Overview")

st.markdown(
    """
    **NeuralRetail Analytics** is an end-to-end retail intelligence system
    created to analyse customer behaviour, sales performance, future demand,
    churn risk and product movement.

    The platform converts raw transaction data into business-focused insights
    that can support marketing, customer retention, forecasting and inventory
    decisions.
    """
)

# -----------------------------
# Technologies and models
# -----------------------------
left, right = st.columns(2)

with left:
    st.subheader("Technologies Used")

    st.markdown(
        """
        - Python
        - Pandas and NumPy
        - Scikit-learn
        - Prophet
        - Plotly
        - Streamlit
        - Joblib
        """
    )

with right:
    st.subheader("Models and Techniques")

    st.markdown(
        """
        - Exploratory Data Analysis
        - RFM Customer Analysis
        - K-Means Customer Segmentation
        - Prophet Demand Forecasting
        - Random Forest Churn Prediction
        - Product Demand Classification
        """
    )

st.divider()

# -----------------------------
# Revenue summary
# -----------------------------
st.subheader("Sales Performance")

monthly_sales = sales.dropna(
    subset=["InvoiceDate"]
).copy()

monthly_sales["Month"] = (
    monthly_sales["InvoiceDate"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    monthly_sales.groupby("Month")["Revenue"]
    .sum()
    .reset_index()
)

sales_fig = px.bar(
    monthly_sales,
    x="Month",
    y="Revenue",
    title="Monthly Revenue Performance"
)

sales_fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Revenue (£)"
)

st.plotly_chart(
    sales_fig,
    use_container_width=True
)

# -----------------------------
# Key findings
# -----------------------------
st.subheader("Key Business Findings")

top_country = (
    sales.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
)

top_product = (
    inventory.sort_values(
        "TotalRevenue",
        ascending=False
    )
    .iloc[0]["Description"]
)

highest_forecast = forecast["yhat"].max()

findings_left, findings_right = st.columns(2)

with findings_left:
    st.success(
        f"**Top Revenue Market:** {top_country}"
    )

    st.info(
        f"**Top Revenue Product:** {top_product}"
    )

    st.warning(
        f"**Customer Churn Rate:** {churn_rate:.2f}%"
    )

with findings_right:
    st.success(
        f"**Average 30-Day Forecast:** £{forecast_average:,.0f}"
    )

    st.info(
        f"**Highest Predicted Daily Revenue:** £{highest_forecast:,.0f}"
    )

    st.warning(
        "Days Since Last Purchase is the strongest churn indicator."
    )

# -----------------------------
# Segmentation summary
# -----------------------------
st.subheader("Customer Segment Summary")

if "Cluster" in segments.columns:
    segment_names = {
        0: "Regular Customers",
        1: "At-Risk Customers",
        2: "VIP Champions",
        3: "Loyal High-Value Customers"
    }

    segments["Segment"] = (
        segments["Cluster"]
        .map(segment_names)
        .fillna("Other Segment")
    )

    segment_summary = (
        segments.groupby("Segment")
        .agg(
            Customers=("Segment", "size"),
            AverageRecency=("Recency", "mean"),
            AverageFrequency=("Frequency", "mean"),
            AverageMonetary=("Monetary", "mean")
        )
        .reset_index()
    )

    for column in [
        "AverageRecency",
        "AverageFrequency",
        "AverageMonetary"
    ]:
        segment_summary[column] = (
            segment_summary[column].round(2)
        )

    st.dataframe(
        segment_summary,
        use_container_width=True,
        hide_index=True
    )
else:
    st.info(
        "Cluster information is unavailable in the segmentation dataset."
    )

# -----------------------------
# Business recommendations
# -----------------------------
st.subheader("Strategic Recommendations")

st.markdown(
    """
    1. **Retain high-value customers** by offering premium rewards,
       personalised recommendations and early access to selected products.

    2. **Re-engage at-risk customers** with reminder campaigns,
       limited-time discounts and targeted communication.

    3. **Increase stock availability** for consistently high-demand products
       and maintain appropriate safety-stock levels.

    4. **Reduce excess inventory** for slow-moving products through bundles,
       discounts or lower reorder quantities.

    5. **Use the sales forecast** to support purchasing, staffing and
       promotional planning.

    6. **Monitor inactive customers regularly**, because recency is the
       strongest signal of churn risk.
    """
)

# -----------------------------
# Project outcome
# -----------------------------
st.subheader("Project Outcome")

st.markdown(
    """
    The project successfully combines descriptive, predictive and prescriptive
    analytics in one commercial-style dashboard.

    It enables decision-makers to:

    - track revenue and order performance,
    - identify valuable customer groups,
    - estimate future demand,
    - recognise churn-prone customers,
    - and optimise product-level inventory decisions.
    """
)

# -----------------------------
# Download summary
# -----------------------------
report_data = pd.DataFrame({
    "Metric": [
        "Total Revenue",
        "Total Orders",
        "Total Customers",
        "Total Products",
        "Churn Rate",
        "Average 30-Day Forecast",
        "Top Revenue Market",
        "Top Revenue Product"
    ],
    "Value": [
        f"£{total_revenue:,.2f}",
        total_orders,
        total_customers,
        total_products,
        f"{churn_rate:.2f}%",
        f"£{forecast_average:,.2f}",
        top_country,
        top_product
    ]
})

csv_data = report_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Executive Summary",
    data=csv_data,
    file_name="executive_summary.csv",
    mime="text/csv"
)

st.caption(
    "NeuralRetail Analytics | End-to-End Retail Intelligence Platform"
)
