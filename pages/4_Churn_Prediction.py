
import streamlit as st
import pandas as pd
import plotly.express as px
import joblib
from pathlib import Path

st.set_page_config(
    page_title="Churn Prediction",
    page_icon="⚠️",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "customer_churn.csv"
MODEL_PATH = BASE_DIR / "models" / "churn_model.pkl"


@st.cache_data
def load_churn_data(file_path):
    return pd.read_csv(file_path)


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


try:
    customer_data = load_churn_data(str(DATA_PATH))
    churn_model = load_model()
except Exception as error:
    st.error(f"Unable to load churn data or model: {error}")
    st.stop()


required_columns = [
    "TotalOrders",
    "TotalRevenue",
    "DaysSinceLastPurchase",
    "Churn"
]

missing_columns = [
    column for column in required_columns
    if column not in customer_data.columns
]

if missing_columns:
    st.error(
        "Missing required columns: "
        + ", ".join(missing_columns)
    )
    st.write("Available columns:", list(customer_data.columns))
    st.stop()


st.title("⚠️ Churn Prediction")
st.caption(
    "Identify customers who are likely to stop purchasing."
)

# -----------------------------
# Sidebar filter
# -----------------------------
st.sidebar.header("Churn Filters")

status_filter = st.sidebar.selectbox(
    "Select customer status",
    options=[
        "All Customers",
        "Active Customers",
        "Churned Customers"
    ]
)

filtered_data = customer_data.copy()

if status_filter == "Active Customers":
    filtered_data = filtered_data[
        filtered_data["Churn"] == 0
    ]
elif status_filter == "Churned Customers":
    filtered_data = filtered_data[
        filtered_data["Churn"] == 1
    ]

if filtered_data.empty:
    st.warning("No customer records match the selected filter.")
    st.stop()

# -----------------------------
# KPI cards
# -----------------------------
total_customers = len(customer_data)
churned_customers = int(customer_data["Churn"].sum())
active_customers = total_customers - churned_customers

churn_rate = (
    churned_customers / total_customers * 100
    if total_customers > 0
    else 0
)

average_inactivity = customer_data[
    "DaysSinceLastPurchase"
].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Customers",
    f"{total_customers:,}"
)

c2.metric(
    "Active Customers",
    f"{active_customers:,}"
)

c3.metric(
    "Churned Customers",
    f"{churned_customers:,}"
)

c4.metric(
    "Churn Rate",
    f"{churn_rate:.2f}%"
)

st.divider()

# -----------------------------
# Churn distribution
# -----------------------------
left, right = st.columns(2)

with left:
    churn_distribution = (
        customer_data["Churn"]
        .value_counts()
        .rename(index={0: "Active", 1: "Churned"})
        .reset_index()
    )

    churn_distribution.columns = [
        "Customer Status",
        "Customers"
    ]

    churn_fig = px.pie(
        churn_distribution,
        names="Customer Status",
        values="Customers",
        title="Customer Churn Distribution",
        hole=0.45
    )

    st.plotly_chart(
        churn_fig,
        use_container_width=True
    )

with right:
    inactivity_fig = px.histogram(
        customer_data,
        x="DaysSinceLastPurchase",
        color=customer_data["Churn"].map(
            {0: "Active", 1: "Churned"}
        ),
        nbins=30,
        title="Customer Inactivity Distribution",
        labels={
            "DaysSinceLastPurchase":
                "Days Since Last Purchase",
            "color": "Customer Status"
        }
    )

    st.plotly_chart(
        inactivity_fig,
        use_container_width=True
    )

# -----------------------------
# Feature importance
# -----------------------------
st.subheader("Churn Model Feature Importance")

feature_names = [
    "TotalOrders",
    "TotalRevenue",
    "DaysSinceLastPurchase"
]

if hasattr(churn_model, "feature_importances_"):
    importance_df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": churn_model.feature_importances_
    }).sort_values(
        "Importance",
        ascending=True
    )

    importance_fig = px.bar(
        importance_df,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Factors Influencing Customer Churn"
    )

    st.plotly_chart(
        importance_fig,
        use_container_width=True
    )
else:
    st.info(
        "Feature importance is unavailable for this model."
    )

# -----------------------------
# Manual prediction tool
# -----------------------------
st.subheader("Predict Customer Churn")

with st.form("churn_prediction_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        total_orders = st.number_input(
            "Total Orders",
            min_value=0,
            value=5,
            step=1
        )

    with col2:
        total_revenue = st.number_input(
            "Total Revenue (£)",
            min_value=0.0,
            value=1000.0,
            step=100.0
        )

    with col3:
        days_since_last_purchase = st.number_input(
            "Days Since Last Purchase",
            min_value=0,
            value=30,
            step=1
        )

    predict_button = st.form_submit_button(
        "Predict Churn Risk"
    )

if predict_button:
    prediction_input = pd.DataFrame({
        "TotalOrders": [total_orders],
        "TotalRevenue": [total_revenue],
        "DaysSinceLastPurchase": [
            days_since_last_purchase
        ]
    })

    prediction = churn_model.predict(
        prediction_input
    )[0]

    if hasattr(churn_model, "predict_proba"):
        probability = churn_model.predict_proba(
            prediction_input
        )[0][1]

        st.metric(
            "Estimated Churn Probability",
            f"{probability * 100:.2f}%"
        )

    if prediction == 1:
        st.error(
            "High churn risk: this customer may stop purchasing."
        )
    else:
        st.success(
            "Low churn risk: this customer is likely to remain active."
        )

# -----------------------------
# Customer records
# -----------------------------
st.subheader("Customer Risk Records")

display_data = filtered_data.copy()

display_data["CustomerStatus"] = (
    display_data["Churn"]
    .map({0: "Active", 1: "Churned"})
)

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

# -----------------------------
# Download
# -----------------------------
csv_data = display_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Churn Report",
    data=csv_data,
    file_name="customer_churn_report.csv",
    mime="text/csv"
)

st.caption(
    f"Average inactivity period: "
    f"{average_inactivity:.2f} days."
)
