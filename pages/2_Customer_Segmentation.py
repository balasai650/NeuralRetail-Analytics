
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Customer Segmentation",
    page_icon="👥",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "customer_segments.csv"


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)

    # Handle index column if saved from RFM dataframe
    unnamed_columns = [
        column for column in data.columns
        if column.lower().startswith("unnamed")
    ]

    if unnamed_columns:
        data = data.rename(
            columns={unnamed_columns[0]: "CustomerID"}
        )

    # Standardize cluster column name
    cluster_candidates = [
        column for column in data.columns
        if column.lower() in ["cluster", "cluster_label", "segment"]
    ]

    if cluster_candidates:
        data = data.rename(
            columns={cluster_candidates[0]: "Cluster"}
        )

    return data


try:
    rfm = load_data()
except Exception as error:
    st.error(f"Unable to load segmentation data: {error}")
    st.stop()


required_columns = ["Recency", "Frequency", "Monetary", "Cluster"]

missing_columns = [
    column for column in required_columns
    if column not in rfm.columns
]

if missing_columns:
    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )
    st.write("Available columns:", list(rfm.columns))
    st.stop()


segment_names = {
    0: "Regular Customers",
    1: "At-Risk Customers",
    2: "VIP Champions",
    3: "Loyal High-Value Customers"
}

rfm["Segment"] = rfm["Cluster"].map(segment_names)

rfm["Segment"] = rfm["Segment"].fillna(
    "Other Segment"
)

st.title("👥 Customer Segmentation")
st.caption(
    "RFM-based customer groups created using K-Means clustering."
)

# -----------------------------
# Sidebar filter
# -----------------------------
st.sidebar.header("Segmentation Filters")

segment_options = sorted(
    rfm["Segment"].dropna().unique()
)

selected_segments = st.sidebar.multiselect(
    "Select customer segments",
    options=segment_options,
    default=segment_options
)

filtered_rfm = rfm[
    rfm["Segment"].isin(selected_segments)
].copy()

if filtered_rfm.empty:
    st.warning("No customers match the selected segments.")
    st.stop()

# -----------------------------
# KPI cards
# -----------------------------
total_customers = len(filtered_rfm)

vip_customers = (
    filtered_rfm["Segment"]
    .eq("VIP Champions")
    .sum()
)

at_risk_customers = (
    filtered_rfm["Segment"]
    .eq("At-Risk Customers")
    .sum()
)

average_customer_value = filtered_rfm["Monetary"].mean()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col2.metric(
    "VIP Champions",
    f"{vip_customers:,}"
)

col3.metric(
    "At-Risk Customers",
    f"{at_risk_customers:,}"
)

col4.metric(
    "Average Customer Value",
    f"£{average_customer_value:,.2f}"
)

st.markdown("---")

# -----------------------------
# Segment distribution
# -----------------------------
left, right = st.columns(2)

with left:
    segment_distribution = (
        filtered_rfm["Segment"]
        .value_counts()
        .reset_index()
    )

    segment_distribution.columns = [
        "Segment",
        "Customers"
    ]

    distribution_fig = px.pie(
        segment_distribution,
        names="Segment",
        values="Customers",
        title="Customer Segment Distribution",
        hole=0.45
    )

    st.plotly_chart(
        distribution_fig,
        use_container_width=True
    )

with right:
    cluster_summary = (
        filtered_rfm.groupby("Segment")
        .agg(
            Recency=("Recency", "mean"),
            Frequency=("Frequency", "mean"),
            Monetary=("Monetary", "mean"),
            Customers=("Segment", "size")
        )
        .reset_index()
    )

    monetary_fig = px.bar(
        cluster_summary,
        x="Segment",
        y="Monetary",
        title="Average Monetary Value by Segment"
    )

    monetary_fig.update_layout(
        xaxis_title="Customer Segment",
        yaxis_title="Average Monetary Value (£)"
    )

    st.plotly_chart(
        monetary_fig,
        use_container_width=True
    )

# -----------------------------
# RFM visualizations
# -----------------------------
left, right = st.columns(2)

with left:
    scatter_fig = px.scatter(
        filtered_rfm,
        x="Recency",
        y="Monetary",
        color="Segment",
        size="Frequency",
        hover_data=[
            "Frequency",
            "Cluster"
        ],
        title="Recency vs Monetary Value"
    )

    scatter_fig.update_layout(
        xaxis_title="Recency (Days)",
        yaxis_title="Monetary Value (£)"
    )

    st.plotly_chart(
        scatter_fig,
        use_container_width=True
    )

with right:
    frequency_fig = px.bar(
        cluster_summary,
        x="Segment",
        y="Frequency",
        title="Average Purchase Frequency by Segment"
    )

    frequency_fig.update_layout(
        xaxis_title="Customer Segment",
        yaxis_title="Average Purchase Frequency"
    )

    st.plotly_chart(
        frequency_fig,
        use_container_width=True
    )

# -----------------------------
# Segment summary
# -----------------------------
st.subheader("Segment Summary")

summary_display = cluster_summary.copy()

summary_display["Recency"] = (
    summary_display["Recency"].round(2)
)

summary_display["Frequency"] = (
    summary_display["Frequency"].round(2)
)

summary_display["Monetary"] = (
    summary_display["Monetary"].round(2)
)

st.dataframe(
    summary_display,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Business recommendations
# -----------------------------
st.subheader("Business Recommendations")

recommendations = {
    "VIP Champions":
        "Provide premium rewards, exclusive offers and early product access.",

    "Loyal High-Value Customers":
        "Use loyalty programmes, bundles and personalised recommendations.",

    "Regular Customers":
        "Encourage repeat purchases through targeted promotions and cross-selling.",

    "At-Risk Customers":
        "Launch re-engagement campaigns, discount offers and reminder emails."
}

for segment in selected_segments:
    recommendation = recommendations.get(
        segment,
        "Review this segment and design a targeted engagement strategy."
    )

    st.info(
        f"**{segment}:** {recommendation}"
    )

# -----------------------------
# Customer table
# -----------------------------
st.subheader("Customer Segment Records")

display_columns = [
    column
    for column in [
        "CustomerID",
        "Recency",
        "Frequency",
        "Monetary",
        "Cluster",
        "Segment"
    ]
    if column in filtered_rfm.columns
]

st.dataframe(
    filtered_rfm[display_columns],
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# CSV download
# -----------------------------
csv_data = filtered_rfm[
    display_columns
].to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Customer Segmentation Report",
    data=csv_data,
    file_name="customer_segmentation_report.csv",
    mime="text/csv"
)

st.caption(
    f"Displaying {len(filtered_rfm):,} customer records."
)
