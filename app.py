import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import glob
import os

st.set_page_config(
    page_title="Stock Exchange Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Exchange Price Analysis")
st.write("Analyze stock market prices and visualize price movements.")

uploaded_file = st.file_uploader(
    "Upload Stock Exchange CSV Dataset",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    files = glob.glob("/kaggle/input/**/*.csv", recursive=True)

    if files:
        df = pd.read_csv(files[0])
        st.info("Using available dataset.")
    else:
        st.warning("Please upload your stock exchange CSV file.")
        st.stop()

df.columns = df.columns.str.strip()

st.subheader("Dataset Preview")
st.dataframe(df.head(10), use_container_width=True)

date_col = next(
    (c for c in df.columns if c.lower() in
     ["date", "datetime", "timestamp"]),
    None
)

close_col = next(
    (c for c in df.columns if c.lower() in
     ["close", "closing_price", "adj close", "adj_close"]),
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
    st.error("No valid stock price data found.")
    st.stop()

df["Price Change"] = df[close_col].diff()

# Price Summary
latest_price = df[close_col].iloc[-1]
highest_price = df[close_col].max()
lowest_price = df[close_col].min()

previous_price = (
    df[close_col].iloc[-2] if len(df) > 1 else latest_price
)

price_difference = latest_price - previous_price

col1, col2, col3 = st.columns(3)

col1.metric(
    "Latest Closing Price",
    f"{latest_price:,.2f}",
    f"{price_difference:+,.2f}"
)

col2.metric("Highest Price", f"{highest_price:,.2f}")
col3.metric("Lowest Price", f"{lowest_price:,.2f}")

# Closing Price Graph
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
    title="Stock Closing Price Over Time",
    xaxis_title="Date / Trading Day",
    yaxis_title="Stock Price",
    template="plotly_dark",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# Price Up and Down Graph
st.subheader("📊 Price Increase and Decrease")

colors = [
    "green" if value >= 0 else "red"
    for value in df["Price Change"].fillna(0)
]

fig2 = go.Figure()

fig2.add_trace(
    go.Bar(
        x=df[x_col],
        y=df["Price Change"].fillna(0),
        marker_color=colors,
        name="Price Change"
    )
)

fig2.update_layout(
    title="Price Change Between Consecutive Rows",
    xaxis_title="Date / Trading Day",
    yaxis_title="Price Change",
    template="plotly_dark"
)

st.plotly_chart(fig2, use_container_width=True)

# Market Statistics
increased = int((df["Price Change"] > 0).sum())
decreased = int((df["Price Change"] < 0).sum())

col1, col2 = st.columns(2)

col1.metric("Price Increased", increased)
col2.metric("Price Decreased", decreased)

# Dataset Download
st.subheader("📁 Analyzed Dataset")

st.dataframe(df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Analyzed CSV",
    data=csv,
    file_name="stock_analysis.csv",
    mime="text/csv"
)
