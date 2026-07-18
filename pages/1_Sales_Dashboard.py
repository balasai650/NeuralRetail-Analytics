
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "online_retail.csv"


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)

    data["InvoiceDate"] = pd.to_datetime(
        data["InvoiceDate"],
        errors="coerce"
    )

    if "Revenue" not in data.columns:
        data["Revenue"] = data["Quantity"] * data["Price"]

    return data


try:
    df = load_data()
except Exception as error:
    st.error(f"Unable to load sales data: {error}")
    st.stop()


st.title("📊 Sales Dashboard")
st.caption("Explore revenue, orders, countries and product performance.")

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Sales Filters")

valid_dates = df["InvoiceDate"].dropna()

if valid_dates.empty:
    st.error("No valid invoice dates are available.")
    st.stop()

minimum_date = valid_dates.min().date()
maximum_date = valid_dates.max().date()

selected_dates = st.sidebar.date_input(
    "Select date range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date
)

countries = sorted(df["Country"].dropna().astype(str).unique())

selected_countries = st.sidebar.multiselect(
    "Select countries",
    options=countries,
    default=countries
)

# Handle selected date range
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = minimum_date
    end_date = maximum_date

filtered_df = df[
    (df["InvoiceDate"].dt.date >= start_date)
    & (df["InvoiceDate"].dt.date <= end_date)
].copy()

if selected_countries:
    filtered_df = filtered_df[
        filtered_df["Country"].astype(str).isin(selected_countries)
    ]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# -----------------------------
# KPI cards
# -----------------------------
total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["Invoice"].nunique()
total_customers = filtered_df["Customer ID"].nunique()
average_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Revenue",
    f"£{total_revenue:,.0f}"
)

col2.metric(
    "Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Customers",
    f"{total_customers:,}"
)

col4.metric(
    "Average Order Value",
    f"£{average_order_value:,.2f}"
)

st.markdown("---")

# -----------------------------
# Daily revenue trend
# -----------------------------
daily_sales = (
    filtered_df.dropna(subset=["InvoiceDate"])
    .groupby(filtered_df["InvoiceDate"].dt.date)
    .agg(
        Revenue=("Revenue", "sum"),
        Orders=("Invoice", "nunique")
    )
    .reset_index()
)

daily_sales.columns = ["Date", "Revenue", "Orders"]

revenue_fig = px.line(
    daily_sales,
    x="Date",
    y="Revenue",
    title="Daily Revenue Trend",
    markers=True
)

revenue_fig.update_layout(
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="Revenue (£)"
)

st.plotly_chart(
    revenue_fig,
    use_container_width=True
)

# -----------------------------
# Monthly revenue and country sales
# -----------------------------
left, right = st.columns(2)

with left:
    monthly_sales = filtered_df.copy()

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

    monthly_fig = px.bar(
        monthly_sales,
        x="Month",
        y="Revenue",
        title="Monthly Revenue"
    )

    monthly_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (£)"
    )

    st.plotly_chart(
        monthly_fig,
        use_container_width=True
    )

with right:
    country_sales = (
        filtered_df.groupby("Country")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    country_fig = px.bar(
        country_sales,
        x="Revenue",
        y="Country",
        orientation="h",
        title="Top 10 Countries by Revenue"
    )

    country_fig.update_layout(
        xaxis_title="Revenue (£)",
        yaxis_title="Country",
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        country_fig,
        use_container_width=True
    )

# -----------------------------
# Top products and order trend
# -----------------------------
left, right = st.columns(2)

with left:
    top_products = (
        filtered_df.groupby("Description")
        .agg(
            Quantity=("Quantity", "sum"),
            Revenue=("Revenue", "sum")
        )
        .sort_values("Revenue", ascending=False)
        .head(10)
        .reset_index()
    )

    product_fig = px.bar(
        top_products,
        x="Revenue",
        y="Description",
        orientation="h",
        title="Top 10 Products by Revenue"
    )

    product_fig.update_layout(
        xaxis_title="Revenue (£)",
        yaxis_title="Product",
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        product_fig,
        use_container_width=True
    )

with right:
    orders_fig = px.area(
        daily_sales,
        x="Date",
        y="Orders",
        title="Daily Order Volume"
    )

    orders_fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Orders",
        hovermode="x unified"
    )

    st.plotly_chart(
        orders_fig,
        use_container_width=True
    )

# -----------------------------
# Download filtered data
# -----------------------------
st.subheader("Download Sales Report")

download_columns = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
    "Revenue"
]

available_columns = [
    column
    for column in download_columns
    if column in filtered_df.columns
]

csv_data = filtered_df[available_columns].to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Sales Data",
    data=csv_data,
    file_name="filtered_sales_report.csv",
    mime="text/csv"
)

st.caption(
    f"Showing {len(filtered_df):,} transaction records "
    f"from {start_date} to {end_date}."
)
