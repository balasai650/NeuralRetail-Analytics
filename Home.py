import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# =========================================================
# Page configuration
# =========================================================
st.set_page_config(
    page_title="NeuralRetail Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# File paths
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "online_retail.csv"


# =========================================================
# Professional styling
# =========================================================
st.markdown(
    """
    <style>
        /* Main page spacing */
        .block-container {
            padding-top: 4.5rem;
            padding-bottom: 3rem;
            max-width: 1450px;
        }

        /* Main title */
        .main-title {
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1.25;
            margin-top: 0.5rem;
            margin-bottom: 0.4rem;
        }

        /* Subtitle */
        .subtitle {
            font-size: 1.05rem;
            color: #7a7a7a;
            margin-top: 0;
            margin-bottom: 1.5rem;
        }

        /* Small information badges */
        .info-badge {
            display: inline-block;
            padding: 6px 12px;
            margin-right: 8px;
            margin-bottom: 10px;
            border-radius: 20px;
            border: 1px solid rgba(128, 128, 128, 0.25);
            background-color: rgba(128, 128, 128, 0.07);
            font-size: 0.85rem;
        }

        /* Streamlit KPI cards */
        [data-testid="stMetric"] {
            padding: 18px;
            border-radius: 12px;
            border: 1px solid rgba(128, 128, 128, 0.22);
            background-color: rgba(128, 128, 128, 0.06);
        }

        [data-testid="stMetricLabel"] {
            font-weight: 600;
        }

        /* Insight cards */
        .insight-card {
            padding: 18px 20px;
            min-height: 105px;
            border-radius: 12px;
            border: 1px solid rgba(79, 139, 249, 0.25);
            background-color: rgba(79, 139, 249, 0.06);
        }

        .insight-label {
            font-size: 0.85rem;
            color: #777777;
            margin-bottom: 7px;
        }

        .insight-value {
            font-size: 1.05rem;
            font-weight: 650;
            line-height: 1.4;
        }

        /* Module cards */
        .module-card {
            padding: 20px;
            min-height: 170px;
            border-radius: 12px;
            border: 1px solid rgba(128, 128, 128, 0.22);
            background-color: rgba(128, 128, 128, 0.04);
            margin-bottom: 15px;
        }

        .module-card h3 {
            font-size: 1.05rem;
            margin-top: 0;
            margin-bottom: 10px;
        }

        .module-card p {
            color: #777777;
            font-size: 0.92rem;
            line-height: 1.55;
            margin-bottom: 0;
        }

        /* Sidebar spacing */
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Data loading
# =========================================================
@st.cache_data(show_spinner="Loading retail data...")
def load_home_data(file_path: str) -> pd.DataFrame:
    data = pd.read_csv(file_path)

    if "InvoiceDate" in data.columns:
        data["InvoiceDate"] = pd.to_datetime(
            data["InvoiceDate"],
            errors="coerce"
        )

    if "Revenue" not in data.columns:
        if {"Quantity", "Price"}.issubset(data.columns):
            data["Revenue"] = data["Quantity"] * data["Price"]

        elif {"Quantity", "UnitPrice"}.issubset(data.columns):
            data["Revenue"] = data["Quantity"] * data["UnitPrice"]

        else:
            raise ValueError(
                "Revenue cannot be calculated because the required "
                "price and quantity columns are missing."
            )

    return data


try:
    df = load_home_data(str(DATA_PATH))

except FileNotFoundError:
    st.error(
        "The dataset was not found. Please confirm that "
        "`data/online_retail.csv` exists."
    )
    st.stop()

except Exception as error:
    st.error(f"Unable to load the retail dataset: {error}")
    st.stop()


# =========================================================
# Detect column names
# =========================================================
invoice_column = next(
    (
        column
        for column in ["Invoice", "InvoiceNo"]
        if column in df.columns
    ),
    None
)

customer_column = next(
    (
        column
        for column in ["Customer ID", "CustomerID"]
        if column in df.columns
    ),
    None
)

product_column = next(
    (
        column
        for column in ["StockCode", "ProductID"]
        if column in df.columns
    ),
    None
)


# =========================================================
# Sidebar
# =========================================================
st.sidebar.markdown("## 🛍️ NeuralRetail")
st.sidebar.caption("Commercial Retail Analytics Platform")

st.sidebar.markdown("---")

st.sidebar.info(
    "Use the navigation menu to explore sales performance, "
    "customer segments, demand forecasts, churn risk and inventory."
)


# =========================================================
# Header
# =========================================================
st.markdown(
    '<p class="main-title">NeuralRetail Analytics</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class="subtitle">
        AI-powered retail intelligence for sales, customers,
        demand forecasting and inventory decisions.
    </p>
    """,
    unsafe_allow_html=True
)


# =========================================================
# Dataset information
# =========================================================
if "InvoiceDate" in df.columns:
    valid_dates = df["InvoiceDate"].dropna()
else:
    valid_dates = pd.Series(dtype="datetime64[ns]")

record_count = len(df)

if not valid_dates.empty:
    start_date = valid_dates.min().strftime("%d %b %Y")
    end_date = valid_dates.max().strftime("%d %b %Y")

    st.markdown(
        f"""
        <span class="info-badge">
            📅 {start_date} – {end_date}
        </span>

        <span class="info-badge">
            📊 {record_count:,} transaction records
        </span>
        """,
        unsafe_allow_html=True
    )

else:
    st.markdown(
        f"""
        <span class="info-badge">
            📊 {record_count:,} transaction records
        </span>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# KPI calculations
# =========================================================
total_revenue = df["Revenue"].sum()

total_orders = (
    df[invoice_column].nunique()
    if invoice_column
    else 0
)

total_customers = (
    df[customer_column].nunique()
    if customer_column
    else 0
)

total_products = (
    df[product_column].nunique()
    if product_column
    else 0
)


# =========================================================
# KPI cards
# =========================================================
st.markdown("### Business Performance")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Total Revenue",
        value=f"£{total_revenue:,.0f}"
    )

with kpi2:
    st.metric(
        label="Total Orders",
        value=f"{total_orders:,}"
    )

with kpi3:
    st.metric(
        label="Total Customers",
        value=f"{total_customers:,}"
    )

with kpi4:
    st.metric(
        label="Total Products",
        value=f"{total_products:,}"
    )


# =========================================================
# Revenue trend
# =========================================================
st.markdown("---")
st.markdown("### Overall Revenue Trend")

if "InvoiceDate" in df.columns:

    revenue_data = df.dropna(
        subset=["InvoiceDate", "Revenue"]
    ).copy()

    revenue_data["Date"] = revenue_data["InvoiceDate"].dt.date

    daily_revenue = (
        revenue_data
        .groupby("Date", as_index=False)["Revenue"]
        .sum()
    )

    figure = px.line(
        daily_revenue,
        x="Date",
        y="Revenue"
    )

    figure.update_traces(
        line_width=2
    )

    figure.update_layout(
        height=430,
        margin=dict(
            l=10,
            r=10,
            t=15,
            b=10
        ),
        xaxis_title="Date",
        yaxis_title="Revenue (£)",
        hovermode="x unified",
        showlegend=False
    )

    figure.update_xaxes(
        showgrid=False
    )

    figure.update_yaxes(
        gridcolor="rgba(128,128,128,0.15)"
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )

else:
    st.warning(
        "Revenue trend is unavailable because the InvoiceDate "
        "column is missing."
    )


# =========================================================
# Business insights
# =========================================================
st.markdown("---")
st.markdown("### Key Business Insights")

if "Quantity" in df.columns:
    positive_quantity_data = df[
        df["Quantity"] > 0
    ].copy()
else:
    positive_quantity_data = df.copy()

insight1, insight2, insight3 = st.columns(3)


with insight1:
    if "Country" in df.columns:

        country_revenue = (
            df.dropna(subset=["Country"])
            .groupby("Country")["Revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        top_country = (
            country_revenue.index[0]
            if not country_revenue.empty
            else "Not available"
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">
                    TOP REVENUE MARKET
                </div>

                <div class="insight-value">
                    🌍 {top_country}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-label">
                    TOP REVENUE MARKET
                </div>

                <div class="insight-value">
                    Not available
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


with insight2:
    if {
        "Description",
        "Quantity"
    }.issubset(positive_quantity_data.columns):

        product_sales = (
            positive_quantity_data
            .dropna(subset=["Description"])
            .groupby("Description")["Quantity"]
            .sum()
            .sort_values(ascending=False)
        )

        top_product = (
            str(product_sales.index[0]).title()
            if not product_sales.empty
            else "Not available"
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">
                    TOP-SELLING PRODUCT
                </div>

                <div class="insight-value">
                    📦 {top_product}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-label">
                    TOP-SELLING PRODUCT
                </div>

                <div class="insight-value">
                    Not available
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


with insight3:
    if invoice_column:

        average_order_value = (
            df.groupby(invoice_column)["Revenue"]
            .sum()
            .mean()
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">
                    AVERAGE ORDER VALUE
                </div>

                <div class="insight-value">
                    💳 £{average_order_value:,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-label">
                    AVERAGE ORDER VALUE
                </div>

                <div class="insight-value">
                    Not available
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# Analytics modules
# =========================================================
st.markdown("---")
st.markdown("### Analytics Capabilities")

module1, module2, module3 = st.columns(3)

with module1:
    st.markdown(
        """
        <div class="module-card">
            <h3>📈 Sales Analytics</h3>

            <p>
                Analyse revenue trends, order activity,
                geographic performance and top-performing products.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with module2:
    st.markdown(
        """
        <div class="module-card">
            <h3>👥 Customer Segmentation</h3>

            <p>
                Apply RFM analysis and K-Means clustering to identify
                valuable, loyal, regular and at-risk customers.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with module3:
    st.markdown(
        """
        <div class="module-card">
            <h3>🔮 Demand Forecasting</h3>

            <p>
                Examine future demand and revenue patterns using
                time-series forecasting with Prophet.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


module4, module5, module6 = st.columns(3)

with module4:
    st.markdown(
        """
        <div class="module-card">
            <h3>⚠️ Churn Prediction</h3>

            <p>
                Identify customers with a higher risk of churn using
                a Random Forest classification model.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with module5:
    st.markdown(
        """
        <div class="module-card">
            <h3>📦 Inventory Optimization</h3>

            <p>
                Compare product demand, revenue and order frequency
                to support inventory planning decisions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with module6:
    st.markdown(
        """
        <div class="module-card">
            <h3>📋 Executive Reporting</h3>

            <p>
                Review consolidated business findings, model outcomes
                and data-driven recommendations.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )