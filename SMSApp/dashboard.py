import streamlit as st
import pandas as pd
import plotly.express as px

st.title("💳 My Transaction Dashboard")

# Load CSV
df = pd.read_csv("transactions.csv")

# --- Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Spent", f"₹{df['amount'].sum():,.2f}")
col2.metric("Total Transactions", len(df))
col3.metric("Biggest Transaction", f"₹{df['amount'].max():,.2f}")

# --- Pie Chart: Category wise spend ---
fig1 = px.pie(df, names="credited_to", values="amount", title="Spend by Merchant")
st.plotly_chart(fig1)

# --- Bar Chart: Spend over time ---
fig2 = px.bar(df, x="date", y="amount", title="Spend Over Time")
st.plotly_chart(fig2)

# --- Raw Data ---
st.subheader("All Transactions")
st.dataframe(df)