import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Stock Exchange Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Exchange Price Analysis")
st.write("Automatically displaying stock market data.")

# Automatically load CSV from GitHub repository
CSV_FILE = "stock_exchange.csv"

if not os.path.exists(CSV_FILE):
    st.error("stock_exchange.csv file not found in repository.")
    st.stop()

df = pd.read_csv(CSV_FILE)
df.columns = df.columns.str.strip()

# Find Date and Closing Price columns
date_col = next(
    (c for c in df.columns
     if c.lower() in ["date", "datetime", "timestamp"]),
    None
)

close_col = next(
    (c for c in df.columns
     if c.lower() in ["close", "closing_price", "adj close", "adj_close"]),
    None
)

if close_col is None:
    st.error("Closing price column not found.")
    st.write("Available columns:", df.columns.tolist())
    st.stop()

df[close_col] = pd.to_numeric(df[close_col], errors="coerce")

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col, close_col])
    df = df.sort_values(date_col)
    x_col = date_col
else:
    df = df.dropna(subset=[close_col]).copy()
    df["Trading Day"] = range(1, len(df) + 1)
    x_col = "Trading Day"

df = df.reset_index(drop=True)

if df.empty:
    st.error("No valid stock data available.")
    st.stop()

df["Price Change"] = df[close_col].diff()

# Summary
latest = df[close_col].iloc[-1]
highest = df[close_col].max()
lowest = df[close_col].min()

c1, c2, c3 = st.columns(3)

c1.metric("Latest Closing Price", f"{latest:,.2f}")
c2.metric("Highest Price", f"{highest:,.2f}")
c3.metric("Lowest Price", f"{lowest:,.2f}")

# Stock Price Graph
st.subheader("📈 Stock Price Movement")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df[x_col],
        y=df[close_col],
        mode="lines",
        name="Closing Price"
    )
)

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Date / Trading Day",
    yaxis_title="Stock Price",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Up and Down Graph
st.subheader("📊 Price Increase and Decrease")

changes = df["Price Change"].fillna(0)

colors = [
    "green" if value >= 0 else "red"
    for value in changes
]

fig2 = go.Figure()

fig2.add_trace(
    go.Bar(
        x=df[x_col],
        y=changes,
        marker_color=colors,
        name="Price Change"
    )
)

fig2.update_layout(
    template="plotly_dark",
    xaxis_title="Date / Trading Day",
    yaxis_title="Price Change"
)

st.plotly_chart(fig2, use_container_width=True)

# Statistics
c1, c2 = st.columns(2)

c1.metric("Price Increased", int((changes > 0).sum()))
c2.metric("Price Decreased", int((changes < 0).sum()))

# Dataset
with st.expander("View Stock Dataset"):
    st.dataframe(df, use_container_width=True)

st.success("Stock dataset loaded automatically!")
