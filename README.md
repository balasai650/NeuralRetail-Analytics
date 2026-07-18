# NeuralRetail Analytics

🚀 **Live Demo:**  
https://neuralretail-analytics-endxfvb49jbfczbeb73zwu.streamlit.app

📂 **GitHub Repository:**  
https://github.com/balasai650/NeuralRetail-Analytics

---

## Overview

NeuralRetail Analytics is an end-to-end Retail Intelligence Dashboard built using Python, Streamlit, Plotly, Scikit-learn, and Prophet.

The dashboard analyzes retail transaction data and provides business insights through interactive visualizations and machine learning models.

## Key Features

- 📊 Sales Performance Dashboard
- 👥 Customer Segmentation (RFM + K-Means)
- 📈 Demand Forecasting using Prophet
- 🔍 Customer Churn Prediction using Random Forest
- 📦 Inventory Optimization
- 📑 Executive Business Report
- 📥 CSV Report Downloads
- 🎨 Interactive and Responsive Streamlit Interface

---

## Dashboard Pages

1. Home
2. Sales Dashboard
3. Customer Segmentation
4. Demand Forecasting
5. Churn Prediction
6. Inventory Optimization
7. Executive Report

---

## Machine Learning Models

### Customer Segmentation
- K-Means Clustering
- Features:
  - Recency
  - Frequency
  - Monetary Value (RFM)

### Demand Forecasting
- Facebook Prophet
- Daily Revenue Forecasting

### Customer Churn Prediction
- Random Forest Classifier
- Features:
  - Total Orders
  - Total Revenue
  - Days Since Last Purchase

### Inventory Optimization
Products are categorized into:
- High Demand
- Medium Demand
- Slow Moving

---

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Scikit-learn
- Prophet
- Joblib

---

## Project Structure

```text
NeuralRetail-Analytics/
│
├── Home.py
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
```

---

## Business Insights

- Identify high-value customer segments.
- Forecast future sales trends.
- Predict customers likely to churn.
- Optimize inventory planning.
- Monitor business KPIs through interactive dashboards.

---

## Author

**Vasantha Bala Sai Kishore Babu**

B.Tech – Computer Science & Engineering (Data Science)

MLR Institute of Technology

GitHub: https://github.com/balasai650
