# Stock Analysis Dashboard

A comprehensive stock analysis dashboard built with Streamlit, yfinance, and QuantStats. This application allows users to analyze stocks, create portfolios, and perform detailed technical and risk analysis.

## Features

1. **Technical Analysis**
   - Candlestick charts
   - Multiple technical indicators (Moving Averages, Bollinger Bands, RSI)
   - Volume analysis

2. **Portfolio Analysis**
   - Multiple stock selection
   - Custom portfolio weights
   - Cumulative returns visualization
   - Correlation analysis
   - Key portfolio metrics

3. **Risk Metrics**
   - Comprehensive risk analysis using QuantStats
   - Sharpe and Sortino ratios
   - Drawdown analysis
   - Rolling metrics
   - Monthly returns heatmap
   - Benchmark comparison

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run Home.py
   ```

2. Use the sidebar to:
   - Enter stock tickers (comma-separated)
   - Select date range
   - Adjust portfolio weights
   - Choose technical indicators
   - Select benchmark for comparison

3. Navigate between pages to access different analyses:
   - Home: Overview and basic stock information
   - Technical Analysis: Detailed technical indicators
   - Portfolio Analysis: Portfolio performance and correlation
   - Risk Metrics: Comprehensive risk analysis

## Dependencies

- streamlit
- yfinance
- quantstats
- plotly
- pandas
- numpy
- python-dateutil

## Notes

- Stock data is fetched from Yahoo Finance using the yfinance library
- Risk metrics are calculated using the QuantStats library
- All visualizations are interactive and created using Plotly 