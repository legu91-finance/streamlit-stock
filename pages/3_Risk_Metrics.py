import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import quantstats as qs
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Risk Metrics", page_icon="📊", layout="wide")

# Check if portfolio is configured
if 'tickers' not in st.session_state:
    st.error("Please configure your portfolio in the Home page first!")
    st.stop()

# Benchmark selection
benchmark = st.sidebar.selectbox("Select Benchmark", ["SPY", "^GSPC", "^DJI", "^IXIC"], index=0)

# Main content
st.title("📊 Risk Metrics Analysis")

@st.cache_data
def fetch_data(tickers, benchmark, start_date, end_date):
    data = pd.DataFrame()
    # Fetch stock data
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)['Close']
        data[ticker] = hist
    
    # Fetch benchmark data
    bench = yf.Ticker(benchmark)
    benchmark_data = bench.history(start=start_date, end=end_date)['Close']
    data[benchmark] = benchmark_data
    
    return data

try:
    # Fetch data
    df = fetch_data(st.session_state.tickers, benchmark, st.session_state.start_date, st.session_state.end_date)
    
    # Calculate returns
    returns = df.pct_change()
    
    # Calculate portfolio returns
    portfolio_returns = pd.Series(0, index=returns.index)
    for ticker, weight in st.session_state.weights.items():
        portfolio_returns += returns[ticker] * weight
    
    benchmark_returns = returns[benchmark]
    
    # Calculate metrics
    metrics = {}
    
    # Risk Metrics
    metrics['Sharpe Ratio'] = qs.stats.sharpe(portfolio_returns)
    metrics['Sortino Ratio'] = qs.stats.sortino(portfolio_returns)
    metrics['Max Drawdown'] = qs.stats.max_drawdown(portfolio_returns)
    metrics['Volatility (ann.)'] = qs.stats.volatility(portfolio_returns)
    metrics['Calmar Ratio'] = qs.stats.calmar(portfolio_returns)
    metrics['Value at Risk'] = qs.stats.value_at_risk(portfolio_returns)
    
    # Display metrics in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Metrics")
        for metric, value in list(metrics.items())[:3]:
            st.metric(
                metric,
                f"{value:.2f}" if isinstance(value, float) else value
            )
    
    with col2:
        for metric, value in list(metrics.items())[3:]:
            st.metric(
                metric,
                f"{value:.2f}" if isinstance(value, float) else value
            )
    
    # Drawdown chart
    st.subheader("Drawdown Analysis")
    drawdown = qs.stats.to_drawdown_series(portfolio_returns)
    
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown * 100,
        fill='tozeroy',
        name='Drawdown'
    ))
    
    fig_dd.update_layout(
        title='Portfolio Drawdown',
        yaxis_title='Drawdown (%)',
        xaxis_title='Date',
        template='plotly_dark',
        height=400
    )
    
    st.plotly_chart(fig_dd, use_container_width=True)
    
    # Rolling metrics
    st.subheader("Rolling Metrics")
    
    # Rolling Sharpe ratio
    rolling_sharpe = qs.stats.rolling_sharpe(portfolio_returns, window=252)
    rolling_sortino = qs.stats.rolling_sortino(portfolio_returns, window=252)
    
    fig_rolling = go.Figure()
    
    fig_rolling.add_trace(go.Scatter(
        x=rolling_sharpe.index,
        y=rolling_sharpe,
        name='Rolling Sharpe'
    ))
    
    fig_rolling.add_trace(go.Scatter(
        x=rolling_sortino.index,
        y=rolling_sortino,
        name='Rolling Sortino'
    ))
    
    fig_rolling.update_layout(
        title='Rolling Risk Metrics (1 Year Window)',
        yaxis_title='Ratio',
        xaxis_title='Date',
        template='plotly_dark',
        height=400
    )
    
    st.plotly_chart(fig_rolling, use_container_width=True)
    
    # Monthly returns heatmap
    st.subheader("Monthly Returns Heatmap")
    
    monthly_returns = qs.stats.monthly_returns(portfolio_returns)
    monthly_returns = monthly_returns.fillna(0) * 100
    
    fig_monthly = go.Figure(data=go.Heatmap(
        z=monthly_returns.values,
        x=monthly_returns.columns,
        y=monthly_returns.index,
        colorscale='RdYlGn',
        text=np.round(monthly_returns.values, 1),
        texttemplate='%{text:.1f}%',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig_monthly.update_layout(
        title='Monthly Returns (%)',
        template='plotly_dark',
        height=400
    )
    
    st.plotly_chart(fig_monthly, use_container_width=True)

except Exception as e:
    st.error(f"Error in risk metrics analysis: {str(e)}") 