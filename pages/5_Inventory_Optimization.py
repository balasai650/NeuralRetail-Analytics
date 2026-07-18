
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Inventory Optimization",
    page_icon="📦",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "inventory_summary.csv"


@st.cache_data
def load_inventory_data(file_path):
    return pd.read_csv(file_path)


try:
    inventory = load_inventory_data(str(DATA_PATH))
except Exception as error:
    st.error(f"Unable to load inventory data: {error}")
    st.stop()


required_columns = [
    "StockCode",
    "Description",
    "TotalQuantity",
    "TotalRevenue",
    "TotalOrders"
]

missing_columns = [
    column for column in required_columns
    if column not in inventory.columns
]

if missing_columns:
    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )
    st.write("Available columns:", list(inventory.columns))
    st.stop()


st.title("📦 Inventory Optimization")
st.caption(
    "Analyse product demand, revenue contribution and stock movement."
)

# -----------------------------
# Clean data
# -----------------------------
inventory = inventory.copy()

inventory["Description"] = (
    inventory["Description"]
    .fillna("Unknown Product")
    .astype(str)
)

numeric_columns = [
    "TotalQuantity",
    "TotalRevenue",
    "TotalOrders"
]

for column in numeric_columns:
    inventory[column] = pd.to_numeric(
        inventory[column],
        errors="coerce"
    ).fillna(0)

# -----------------------------
# Demand classification
# -----------------------------
quantity_high = inventory["TotalQuantity"].quantile(0.75)
quantity_low = inventory["TotalQuantity"].quantile(0.25)

revenue_high = inventory["TotalRevenue"].quantile(0.75)

def classify_product(row):
    if (
        row["TotalQuantity"] >= quantity_high
        and row["TotalRevenue"] >= revenue_high
    ):
        return "High Demand"

    if row["TotalQuantity"] <= quantity_low:
        return "Slow Moving"

    return "Medium Demand"


inventory["DemandCategory"] = inventory.apply(
    classify_product,
    axis=1
)

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Inventory Filters")

demand_options = sorted(
    inventory["DemandCategory"].unique()
)

selected_categories = st.sidebar.multiselect(
    "Select demand category",
    options=demand_options,
    default=demand_options
)

minimum_orders = st.sidebar.number_input(
    "Minimum number of orders",
    min_value=0,
    value=0,
    step=1
)

filtered_inventory = inventory[
    inventory["DemandCategory"].isin(
        selected_categories
    )
    & (
        inventory["TotalOrders"]
        >= minimum_orders
    )
].copy()

if filtered_inventory.empty:
    st.warning("No products match the selected filters.")
    st.stop()

# -----------------------------
# KPI cards
# -----------------------------
total_products = len(filtered_inventory)

high_demand_products = (
    filtered_inventory["DemandCategory"]
    .eq("High Demand")
    .sum()
)

slow_moving_products = (
    filtered_inventory["DemandCategory"]
    .eq("Slow Moving")
    .sum()
)

total_inventory_revenue = (
    filtered_inventory["TotalRevenue"].sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Products",
    f"{total_products:,}"
)

col2.metric(
    "High-Demand Products",
    f"{high_demand_products:,}"
)

col3.metric(
    "Slow-Moving Products",
    f"{slow_moving_products:,}"
)

col4.metric(
    "Product Revenue",
    f"£{total_inventory_revenue:,.0f}"
)

st.divider()

# -----------------------------
# Top products
# -----------------------------
left, right = st.columns(2)

with left:
    top_quantity = (
        filtered_inventory
        .sort_values(
            "TotalQuantity",
            ascending=False
        )
        .head(10)
    )

    quantity_fig = px.bar(
        top_quantity,
        x="TotalQuantity",
        y="Description",
        orientation="h",
        title="Top 10 Products by Quantity Sold"
    )

    quantity_fig.update_layout(
        xaxis_title="Total Quantity Sold",
        yaxis_title="Product",
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        quantity_fig,
        use_container_width=True
    )

with right:
    top_revenue = (
        filtered_inventory
        .sort_values(
            "TotalRevenue",
            ascending=False
        )
        .head(10)
    )

    revenue_fig = px.bar(
        top_revenue,
        x="TotalRevenue",
        y="Description",
        orientation="h",
        title="Top 10 Products by Revenue"
    )

    revenue_fig.update_layout(
        xaxis_title="Revenue (£)",
        yaxis_title="Product",
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(
        revenue_fig,
        use_container_width=True
    )

# -----------------------------
# Demand distribution
# -----------------------------
left, right = st.columns(2)

with left:
    demand_distribution = (
        filtered_inventory["DemandCategory"]
        .value_counts()
        .reset_index()
    )

    demand_distribution.columns = [
        "Demand Category",
        "Products"
    ]

    demand_fig = px.pie(
        demand_distribution,
        names="Demand Category",
        values="Products",
        title="Product Demand Distribution",
        hole=0.45
    )

    st.plotly_chart(
        demand_fig,
        use_container_width=True
    )

with right:
    scatter_fig = px.scatter(
        filtered_inventory,
        x="TotalQuantity",
        y="TotalRevenue",
        size="TotalOrders",
        color="DemandCategory",
        hover_name="Description",
        title="Quantity Sold vs Revenue"
    )

    scatter_fig.update_layout(
        xaxis_title="Total Quantity Sold",
        yaxis_title="Total Revenue (£)"
    )

    st.plotly_chart(
        scatter_fig,
        use_container_width=True
    )

# -----------------------------
# Slow-moving products
# -----------------------------
st.subheader("Slow-Moving Products")

slow_products = (
    filtered_inventory[
        filtered_inventory["DemandCategory"]
        == "Slow Moving"
    ]
    .sort_values(
        ["TotalQuantity", "TotalRevenue"],
        ascending=True
    )
)

if slow_products.empty:
    st.info(
        "No slow-moving products match the current filters."
    )
else:
    st.dataframe(
        slow_products[
            [
                "StockCode",
                "Description",
                "TotalQuantity",
                "TotalOrders",
                "TotalRevenue",
                "DemandCategory"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# -----------------------------
# Business recommendations
# -----------------------------
st.subheader("Inventory Recommendations")

st.success(
    "High-demand products should receive higher safety-stock levels "
    "and more frequent replenishment."
)

st.warning(
    "Slow-moving products should be reviewed for discounting, bundling, "
    "reduced reorder quantities or discontinuation."
)

st.info(
    "Medium-demand products should be monitored using regular sales trends "
    "before changing stock levels."
)

# -----------------------------
# Full inventory table
# -----------------------------
st.subheader("Inventory Records")

display_columns = [
    "StockCode",
    "Description",
    "TotalQuantity",
    "TotalRevenue",
    "TotalOrders",
    "DemandCategory"
]

st.dataframe(
    filtered_inventory[display_columns],
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Download
# -----------------------------
csv_data = filtered_inventory[
    display_columns
].to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Inventory Report",
    data=csv_data,
    file_name="inventory_optimization_report.csv",
    mime="text/csv"
)

st.caption(
    f"Displaying {len(filtered_inventory):,} products."
)
