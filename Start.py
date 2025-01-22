import streamlit as st

st.set_page_config(
    page_title="Stock Analysis Dashboard - Documentation",
    page_icon="📚",
    layout="wide"
)

# Header and Quick Tip
st.title("📚 Stock Analysis Dashboard")

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("A powerful tool for stock analysis and portfolio management with advanced features and visualizations.")
with col2:
    st.info("**Quick Tip:** Start with the Portfolio Setup page to configure your investment portfolio!")

# Main Features in Three Columns
st.markdown("## 📱 Main Features")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 1. 💼 Portfolio Setup
    - Add/remove stocks
    - Adjust portfolio weights
    - Access Nasdaq 100 companies
    - View company information
    - Real-time stock data
    """)

with col2:
    st.markdown("""
    ### 2. 📊 Portfolio Analysis
    - Monte Carlo simulation
    - Adjustable forecast (1-10 years)
    - Performance metrics
    - Returns heatmap
    - Correlation analysis
    """)

with col3:
    st.markdown("""
    ### 3. 📈 Risk & Technical
    - Risk metrics calculation
    - Drawdown analysis
    - Technical indicators
    - Interactive charts
    - Volume analysis
    """)

# Tools & Technologies
st.markdown("## 🛠️ Built With")
tech_col1, tech_col2, tech_col3 = st.columns(3)

with tech_col1:
    st.markdown("""
    ### Core
    - Streamlit
    - yfinance
    - QuantStats
    - Plotly
    - Pandas
    """)

with tech_col2:
    st.markdown("""
    ### Features
    - Real-time updates
    - Interactive design
    - Data persistence
    - Custom timeframes
    """)

with tech_col3:
    st.markdown("""
    ### Analysis
    - Monte Carlo
    - Risk metrics
    - Technical indicators
    - Portfolio tracking
    """)

# Quick Start Guide
with st.expander("🚀 Quick Start Guide"):
    st.markdown("""
    1. Configure portfolio in Portfolio Setup
    2. Add stocks and adjust weights
    3. Set analysis timeframe
    4. Explore analysis features
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <i>Built with ❤️ for stock market enthusiasts</i><br>
    <small>Version 1.0</small><br>
    <small>Created by <a href='https://lennartandreasgursky.netlify.app/' target='_blank'>Lennart Andreas Gursky</a></small>
</div>
""", unsafe_allow_html=True) 