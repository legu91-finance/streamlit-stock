import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import numpy as np

st.set_page_config(page_title="Technical Analysis", page_icon="📊", layout="wide")

# Get first ticker from session state for technical analysis
if 'tickers' not in st.session_state:
    st.error("Please configure your portfolio in the Home page first!")
    st.stop()

# Replace single ticker with dropdown selection
ticker = st.sidebar.selectbox(
    "Select Instrument",
    st.session_state.tickers,
    index=0
)

# Technical indicators selection
st.sidebar.subheader("Technical Indicators")
show_ma = st.sidebar.checkbox("Moving Averages", True)
show_bb = st.sidebar.checkbox("Bollinger Bands", False)
show_rsi = st.sidebar.checkbox("RSI", True)

# Fetch data
@st.cache_data
def fetch_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date)
    return df

# Main content
st.title(f"📊 Technical Analysis - {ticker}")

try:
    df = fetch_data(ticker, st.session_state.start_date, st.session_state.end_date)
    
    # Calculate technical indicators
    if show_ma:
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
    
    if show_bb:
        df['BB_middle'] = df['Close'].rolling(window=20).mean()
        df['BB_upper'] = df['BB_middle'] + 2 * df['Close'].rolling(window=20).std()
        df['BB_lower'] = df['BB_middle'] - 2 * df['Close'].rolling(window=20).std()
    
    if show_rsi:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

    # Create candlestick chart
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    ))

    if show_ma:
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name='MA20', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], name='MA50', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], name='MA200', line=dict(color='red')))

    if show_bb:
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], name='BB Upper', line=dict(color='gray', dash='dash')))
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], name='BB Lower', line=dict(color='gray', dash='dash')))

    fig.update_layout(
        title=f'{ticker} Price Chart',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark',
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False  # This will remove the rangeslider which often shows volume
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display RSI if selected
    if show_rsi:
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI'))
        rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
        rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
        rsi_fig.update_layout(
            title='Relative Strength Index (RSI)',
            yaxis_title='RSI',
            xaxis_title='Date',
            template='plotly_dark',
            height=300
        )
        st.plotly_chart(rsi_fig, use_container_width=True)

except Exception as e:
    st.error(f"Error fetching data for {ticker}: {str(e)}") 