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

def calculate_alpha(portfolio_returns, market_returns, rf_rate):
    beta = portfolio_returns.cov(market_returns) / market_returns.var()
    expected_return = rf_rate/252 + beta * (market_returns.mean() - rf_rate/252)
    alpha = portfolio_returns.mean() - expected_return
    return alpha * 252  # Annualized alpha

def calculate_max_drawdown(returns):
    cum_returns = (1 + returns).cumprod()
    rolling_max = cum_returns.expanding().max()
    drawdowns = cum_returns/rolling_max - 1
    return drawdowns.min()

def simulate_portfolio_scenario(portfolio_returns, max_drop, recovery):
    # Simple simulation based on historical volatility
    vol = portfolio_returns.std()
    scenario_return = max_drop + (recovery * np.random.normal(0, vol))
    return scenario_return

def calculate_risk_metrics(portfolio_returns):
    rf_rate = 0.04  # Assume 4% risk-free rate
    excess_returns = portfolio_returns - rf_rate/252
    
    metrics = {
        "Beta": portfolio_returns.cov(market_returns) / market_returns.var(),
        "Alpha": calculate_alpha(portfolio_returns, market_returns, rf_rate),
        "Sortino Ratio": excess_returns.mean() / portfolio_returns[portfolio_returns < 0].std() * np.sqrt(252),
        "Max Drawdown": calculate_max_drawdown(portfolio_returns),
        "Value at Risk (95%)": portfolio_returns.quantile(0.05),
        "Expected Shortfall": portfolio_returns[portfolio_returns <= portfolio_returns.quantile(0.05)].mean()
    }
    return metrics

def plot_correlation_heatmap(returns):
    corr = returns.corr()
    fig = px.imshow(
        corr,
        labels=dict(color="Correlation"),
        color_continuous_scale="RdBu_r",
        aspect="auto",
        template="plotly_dark"
    )
    fig.update_layout(
        title="Asset Correlation Matrix",
        height=500,
        xaxis_title="",
        yaxis_title="",
    )
    # Add correlation values as text annotations
    for i in range(len(corr.index)):
        for j in range(len(corr.columns)):
            fig.add_annotation(
                x=j,
                y=i,
                text=f"{corr.iloc[i, j]:.2f}",
                showarrow=False,
                font=dict(color="white" if abs(corr.iloc[i, j]) < 0.5 else "black")
            )
    return fig

def plot_risk_contribution(returns, weights):
    # Calculate covariance matrix
    cov = returns.cov()
    
    # Calculate portfolio volatility
    port_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
    
    # Calculate marginal contribution to risk
    marginal_contrib = np.dot(cov, weights) / port_vol
    
    # Calculate component contribution to risk
    risk_contrib = np.multiply(marginal_contrib, weights)
    
    # Convert to percentage
    risk_contrib_pct = risk_contrib / risk_contrib.sum() * 100
    
    # Create pie chart
    fig = px.pie(
        values=risk_contrib_pct,
        names=returns.columns,
        title="Risk Contribution by Asset (%)",
        template="plotly_dark"
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>" +
                      "Risk Contribution: %{percent}<br>" +
                      "<extra></extra>"
    )
    
    fig.update_layout(
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def run_monte_carlo_simulation(portfolio_returns, market_returns, n_simulations=1000, n_days=252):
    # Calculate portfolio characteristics
    portfolio_vol = portfolio_returns.std()
    portfolio_mean = portfolio_returns.mean()
    
    # Generate random paths using geometric Brownian motion
    drift = portfolio_mean - (portfolio_vol ** 2) / 2
    daily_returns = np.exp(
        drift + portfolio_vol * np.random.normal(0, 1, size=(n_simulations, n_days))
    )
    
    # Calculate price paths
    initial_portfolio_value = 10000  # Starting at $10000
    price_paths = initial_portfolio_value * np.cumprod(daily_returns, axis=1)
    
    # Calculate statistics for the final values
    final_values = price_paths[:, -1]
    percentiles = np.percentile(final_values, [5, 25, 50, 75, 95])
    
    return price_paths, percentiles

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
    
    st.subheader("Portfolio Metrics")
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



    # After the monthly returns heatmap, add new sections for risk metrics and analysis
    st.subheader("Risk Metrics")
    
    # Fetch market data (S&P 500 as benchmark)
    benchmark = yf.Ticker("^GSPC")
    market_returns = benchmark.history(start=st.session_state.start_date, 
                                     end=st.session_state.end_date)['Close'].pct_change()
    
    # Calculate and display risk metrics
    risk_metrics = calculate_risk_metrics(portfolio_returns)
    
    # Display risk metrics in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Beta", f"{risk_metrics['Beta']:.2f}")
        st.metric("Alpha", f"{risk_metrics['Alpha']:.2%}")
    with col2:
        st.metric("Sortino Ratio", f"{risk_metrics['Sortino Ratio']:.2f}")
        st.metric("Max Drawdown", f"{risk_metrics['Max Drawdown']:.2%}")
    with col3:
        st.metric("Value at Risk (95%)", f"{risk_metrics['Value at Risk (95%)']:.2%}")
        st.metric("Expected Shortfall", f"{risk_metrics['Expected Shortfall']:.2%}")
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
    


    # Correlation Analysis
    st.subheader("Correlation Analysis")
    correlation_fig = plot_correlation_heatmap(returns)
    st.plotly_chart(correlation_fig, use_container_width=True)

    # Risk Contribution Analysis
    st.subheader("Risk Contribution Analysis")
    weights_array = np.array([st.session_state.weights[ticker] for ticker in st.session_state.tickers])
    risk_contrib_fig = plot_risk_contribution(returns, weights_array)
    st.plotly_chart(risk_contrib_fig, use_container_width=True)

    # Scenario Analysis
    st.subheader("Monte Carlo Simulation")

    # Add time period slider
    forecast_years = st.slider(
        "Forecast Period (Years)", 
        min_value=1, 
        max_value=10, 
        value=1, 
        help="Adjust the number of years to forecast into the future"
    )

    # Update simulation with dynamic time period
    n_days = forecast_years * 252  # Convert years to trading days
    price_paths, percentiles = run_monte_carlo_simulation(portfolio_returns, market_returns, n_simulations=1000, n_days=n_days)

    # Create visualization
    fig = go.Figure()

    # Plot a subset of paths for better visualization
    n_paths_to_plot = 100
    random_indices = np.random.choice(len(price_paths), n_paths_to_plot, replace=False)

    # Add individual paths with low opacity
    for idx in random_indices:
        fig.add_trace(go.Scatter(
            y=price_paths[idx],
            x=np.linspace(0, forecast_years, n_days),  # Update x-axis to show years
            mode='lines',
            line=dict(color='rgba(100, 149, 237, 0.1)'),
            showlegend=False
        ))

    # Add percentile lines
    percentile_colors = ['rgba(255,0,0,0.8)', 'rgba(255,165,0,0.8)', 'white', 
                        'rgba(144,238,144,0.8)', 'rgba(0,255,0,0.8)']
    percentile_names = ['5th', '25th', '50th (Median)', '75th', '95th']

    for i, percentile in enumerate([5, 25, 50, 75, 95]):
        y_values = np.percentile(price_paths, percentile, axis=0)
        fig.add_trace(go.Scatter(
            y=y_values,
            x=np.linspace(0, forecast_years, n_days),  # Update x-axis to show years
            mode='lines',
            line=dict(color=percentile_colors[i], width=2),
            name=f'{percentile_names[i]} Percentile'
        ))

    fig.update_layout(
        title=f"{forecast_years}-Year Monte Carlo Simulation (1000 Scenarios)",  # Dynamic title
        template="plotly_dark",
        height=600,
        xaxis_title="Years",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display key statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("5th Percentile", f"${percentiles[0]:,.2f}")
    with col2:
        st.metric("25th Percentile", f"${percentiles[1]:,.2f}")
    with col3:
        st.metric("Median", f"${percentiles[2]:,.2f}")
    with col4:
        st.metric("75th Percentile", f"${percentiles[3]:,.2f}")
    with col5:
        st.metric("95th Percentile", f"${percentiles[4]:,.2f}")

    st.caption(f"""
    This Monte Carlo simulation shows 1000 possible paths your portfolio might take over the next {forecast_years} 
    {'year' if forecast_years == 1 else 'years'}, starting from a $10,000 investment. The colored lines represent different 
    percentiles of outcomes, helping you understand the range of possible returns. The simulation uses your portfolio's 
    historical volatility and returns to generate realistic scenarios.
    """)

except Exception as e:
    st.error(f"Error in portfolio analysis: {str(e)}") 