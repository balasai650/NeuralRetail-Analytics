
# NeuralRetail Analytics

NeuralRetail Analytics is an end-to-end retail intelligence dashboard built using Python, Streamlit, Plotly, Scikit-learn and Prophet.

The project analyses retail transaction data and provides insights related to:

- Sales performance
- Customer segmentation
- Demand forecasting
- Customer churn
- Inventory optimization
- Executive business reporting

## Dashboard Pages

1. Home
2. Sales Dashboard
3. Customer Segmentation
4. Demand Forecasting
5. Churn Prediction
6. Inventory Optimization
7. Executive Report

## Main Features

- Interactive KPI cards
- Plotly charts
- Date filters
- Country filters
- Customer segment filters
- Churn prediction tool
- Product demand classification
- CSV report downloads
- Responsive Streamlit layout

## Machine Learning Models

### Customer Segmentation

K-Means clustering is used with RFM variables:

- Recency
- Frequency
- Monetary value

### Demand Forecasting

Prophet is used to forecast future daily revenue.

### Churn Prediction

A Random Forest classifier predicts whether a customer is likely to churn using:

- Total orders
- Total revenue
- Days since last purchase

### Inventory Optimization

Products are classified as:

- High Demand
- Medium Demand
- Slow Moving

## Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- Prophet
- Plotly
- Streamlit
- Joblib

## Project Structure

```text
NeuralRetail/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── online_retail.csv
│   ├── customer_segments.csv
│   ├── customer_churn.csv
│   ├── inventory_summary.csv
│   └── forecast_results.csv
│
├── models/
│   ├── kmeans_model.pkl
│   └── churn_model.pkl
│
└── pages/
    ├── 1_Sales_Dashboard.py
    ├── 2_Customer_Segmentation.py
    ├── 3_Demand_Forecasting.py
    ├── 4_Churn_Prediction.py
    ├── 5_Inventory_Optimization.py
    └── 6_Executive_Report.py
