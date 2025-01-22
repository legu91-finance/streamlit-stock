import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Portfolio Analysis", page_icon="📊", layout="wide")

# Check if portfolio is configured
if 'tickers' not in st.session_state:
    st.error("Please configure your portfolio in the Home page first!")
    st.stop()

# Main content
st.title("📊 Portfolio Analysis")

@st.cache_data
def fetch_portfolio_data(tickers, start_date, end_date):
    data = pd.DataFrame()
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)['Close']
        data[ticker] = hist
    return data

try:
    # Fetch data
    df = fetch_portfolio_data(st.session_state.tickers, st.session_state.start_date, st.session_state.end_date)
    
    # Calculate daily returns
    returns = df.pct_change()
    
    # Calculate portfolio returns
    portfolio_returns = pd.Series(0, index=returns.index)
    for ticker, weight in st.session_state.weights.items():
        portfolio_returns += returns[ticker] * weight
    
    # Cumulative returns
    cumulative_returns = (1 + returns).cumprod()
    portfolio_cumulative_returns = (1 + portfolio_returns).cumprod()
    

# Portfolio statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Portfolio Return",
            f"{(portfolio_cumulative_returns.iloc[-1] - 1) * 100:.2f}%"
        )
    
    with col2:
        st.metric(
            "Portfolio Volatility",
            f"{portfolio_returns.std() * np.sqrt(252) * 100:.2f}%"
        )
    
    with col3:
        sharpe = np.sqrt(252) * (portfolio_returns.mean() / portfolio_returns.std())
        st.metric(
            "Sharpe Ratio",
            f"{sharpe:.2f}"
        )

    # Plot cumulative returns
    fig = go.Figure()
    
    # Add individual stock returns
    for ticker in st.session_state.tickers:
        fig.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns[ticker],
            name=ticker,
            line=dict(dash='dash')
        ))
    
    # Add portfolio returns
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative_returns.index,
        y=portfolio_cumulative_returns,
        name='Portfolio',
        line=dict(color='white', width=3)
    ))
    
    fig.update_layout(
        title='Cumulative Returns',
        yaxis_title='Return',
        xaxis_title='Date',
        template='plotly_dark',
        height=500
    )
    
    # Add subheader and display cumulative performance plot
    st.subheader("Cumulative Performance")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Performance Heatmap")
    # Monthly returns heatmap
    monthly_returns = portfolio_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
    monthly_returns_df = pd.DataFrame(monthly_returns)
    monthly_returns_df.index = pd.to_datetime(monthly_returns_df.index)
    
    # Create a pivot table with years as rows and months as columns
    monthly_pivot = pd.DataFrame({
        'Year': monthly_returns_df.index.year,
        'Month': monthly_returns_df.index.month,
        'Returns': monthly_returns_df[0]
    }).pivot(index='Year', columns='Month', values='Returns')
    
    # Create month labels
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_pivot.columns = month_labels
    
    # Convert to numpy array for heatmap
    data_array = monthly_pivot.values
    
    fig_returns = go.Figure(data=go.Heatmap(
        z=data_array,
        x=month_labels,
        y=monthly_pivot.index.astype(str),
        colorscale=[
            [0, 'rgb(165,0,38)'],      # Darker red for negative
            [0.4, 'rgb(215,48,39)'],   # Red
            [0.45, 'rgb(244,109,67)'], # Light red
            [0.5, 'rgb(255,255,255)'], # White for zero
            [0.55, 'rgb(171,217,233)'],# Light green
            [0.6, 'rgb(116,173,209)'], # Green
            [1, 'rgb(69,117,180)']     # Dark green for positive
        ],
        text=[[f'{val:.1%}' if pd.notna(val) else '' for val in row] for row in data_array],
        texttemplate='%{text}',
        textfont={"size": 10, "family": "Arial"},  # Reduced font size
        hoverongaps=False,
        hovertemplate='Year: %{y}<br>Month: %{x}<br>Return: %{text}<extra></extra>',
        showscale=True,
        zmid=0
    ))
    
    fig_returns.update_layout(
        title={
            'text': 'Monthly Returns (%)',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        template='plotly_dark',
        height=400,  # Reduced height from 800 to 400
        xaxis_title='',
        yaxis_title='',
        yaxis={'autorange': 'reversed', 'dtick': 1},
        margin=dict(l=50, r=50, t=70, b=50),
        coloraxis_colorbar=dict(
            title="Return",
            tickformat=".0%",
            len=0.9,
            thickness=15,
        )
    )
    
    # Add text with contrasting colors and improved formatting
    for i in range(len(monthly_pivot.index)):
        for j in range(len(monthly_pivot.columns)):
            value = monthly_pivot.iloc[i, j]
            if pd.notna(value):
                color = 'black' if abs(value) < 0.02 else 'white'
                fig_returns.add_annotation(
                    x=j,
                    y=i,
                    text=f'{value:.1%}',
                    showarrow=False,
                    font=dict(
                        color=color, 
                        size=10,  # Reduced font size
                        family='Arial'
                    ),
                    xref='x',
                    yref='y'
                )

    st.plotly_chart(fig_returns, use_container_width=True)
    
    
    

except Exception as e:
    st.error(f"Error in portfolio analysis: {str(e)}") 