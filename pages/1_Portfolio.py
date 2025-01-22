import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Portfolio Setup",
    page_icon="💼",
    layout="wide"
)

# Initialize session state for shared variables
if 'tickers' not in st.session_state:
    st.session_state.tickers = ["AAPL", "MSFT", "GOOGL", "NVDA"]

# When initializing or recalculating weights
def calculate_balanced_weights(tickers):
    num_tickers = len(tickers)
    base_weight = 100 // num_tickers  # Integer division
    remainder = 100 - (base_weight * num_tickers)
    
    weights = {}
    for i, ticker in enumerate(tickers):
        extra = 1 if i < remainder else 0
        weights[ticker] = (base_weight + extra) / 100
    return weights

# Use this function when initializing weights
if 'weights' not in st.session_state:
    st.session_state.weights = calculate_balanced_weights(st.session_state.tickers)

if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now() - timedelta(days=365)
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.now()

# Sidebar setup
st.sidebar.title("Portfolio Setup")

# Stock ticker input
ticker_input = st.sidebar.text_input("Enter Stock Ticker(s) (comma-separated)", ", ".join(st.session_state.tickers))
st.session_state.tickers = [ticker.strip() for ticker in ticker_input.split(",")]

# Date range selection
st.session_state.start_date = st.sidebar.date_input("Start Date", st.session_state.start_date)
st.session_state.end_date = st.sidebar.date_input("End Date", st.session_state.end_date)

# Portfolio weights
st.sidebar.subheader("Portfolio Weights")
total_weight = 0

# Add radio button to choose input method
weight_input_method = st.sidebar.radio("Weight Input Method", ["Sliders", "Text Input"])

# Initialize/reset weights dictionary
weights = {}

for ticker in st.session_state.tickers:
    # Create a horizontal layout for each weight input
    weight_col1, weight_col2 = st.sidebar.columns([4, 1])
    
    # Calculate the correct default weight for this ticker
    num_tickers = len(st.session_state.tickers)
    base_weight = 100 // num_tickers
    remainder = 100 - (base_weight * num_tickers)
    default_weight = base_weight + (1 if st.session_state.tickers.index(ticker) < remainder else 0)
    
    with weight_col1:
        if weight_input_method == "Sliders":
            weight = st.slider(f"{ticker} Weight (%)", 0, 100, default_weight)
        else:
            weight = st.number_input(f"{ticker} Weight (%)", 0, 100, default_weight, step=1)
    
    with weight_col2:
        if st.button("❌", key=f"delete_{ticker}"):
            st.session_state.tickers.remove(ticker)
            st.rerun()
    
    total_weight += weight
    weights[ticker] = weight / 100

# Update session state weights all at once after the loop
st.session_state.weights = weights

# Add a running total display
st.sidebar.markdown(f"**Total Portfolio Weight: {total_weight}%**")
if total_weight != 100:
    st.sidebar.warning("⚠️ Total weight should equal 100%")

# Main content
st.title("💼 Portfolio Setup")
st.write("Configure your portfolio settings in the sidebar.")

# Add a quick start guide
st.info("""
**Quick Start Guide:**
1. Use the sidebar to add or remove stocks
2. Adjust portfolio weights (should total 100%)
3. Set your desired date range
4. Navigate to different analysis pages using the sidebar menu
""")

# Display basic stock info
if st.button("Fetch Stock Data"):
    for ticker in st.session_state.tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        with st.expander(f"{ticker} - Basic Information"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Company Name:**", info.get('longName', 'N/A'))
                st.write("**Sector:**", info.get('sector', 'N/A'))
                st.write("**Industry:**", info.get('industry', 'N/A'))
                
            with col2:
                st.write("**Market Cap:**", f"${info.get('marketCap', 0):,.2f}")
                st.write("**Current Price:**", f"${info.get('currentPrice', 0):,.2f}")
                st.write("**52 Week Range:**", f"${info.get('fiftyTwoWeekLow', 0):,.2f} - ${info.get('fiftyTwoWeekHigh', 0):,.2f}")

# Nasdaq 100 Companies section
st.markdown("### Nasdaq 100 Companies")
search = st.text_input("Search companies", "")

# Define Nasdaq 100 companies
nasdaq100 = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc.',
    'AMZN': 'Amazon.com Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.',
    'TSLA': 'Tesla Inc.',
    'AVGO': 'Broadcom Inc.',
    'PEP': 'PepsiCo Inc.',
    'COST': 'Costco Wholesale Corporation',
    'CSCO': 'Cisco Systems Inc.',
    'AMD': 'Advanced Micro Devices Inc.',
    'TMUS': 'T-Mobile US Inc.',
    'INTC': 'Intel Corporation',
    'QCOM': 'QUALCOMM Incorporated',
    'INTU': 'Intuit Inc.',
    'ADBE': 'Adobe Inc.',
    'TXN': 'Texas Instruments Inc.',
    'NFLX': 'Netflix Inc.',
    'CMCSA': 'Comcast Corporation',
    'HON': 'Honeywell International Inc.',
    'AMAT': 'Applied Materials Inc.',
    'BKNG': 'Booking Holdings Inc.',
    'SBUX': 'Starbucks Corporation',
    'GILD': 'Gilead Sciences Inc.',
    'ADI': 'Analog Devices Inc.',
    'MDLZ': 'Mondelez International Inc.',
    'PYPL': 'PayPal Holdings Inc.',
    'REGN': 'Regeneron Pharmaceuticals Inc.',
    'VRTX': 'Vertex Pharmaceuticals Inc.',
    'ISRG': 'Intuitive Surgical Inc.',
    'LRCX': 'Lam Research Corporation',
    'MU': 'Micron Technology Inc.',
    'ATVI': 'Activision Blizzard Inc.',
    'CSX': 'CSX Corporation',
    'KLAC': 'KLA Corporation',
    'MRVL': 'Marvell Technology Inc.',
    'GOOG': 'Alphabet Inc. Class C',
    'PANW': 'Palo Alto Networks Inc.',
    'KDP': 'Keurig Dr Pepper Inc.',
    'SNPS': 'Synopsys Inc.',
    'CDNS': 'Cadence Design Systems Inc.',
    'NXPI': 'NXP Semiconductors N.V.',
    'FTNT': 'Fortinet Inc.',
    'ADP': 'Automatic Data Processing Inc.',
    'ORLY': "O'Reilly Automotive Inc.",
    'MNST': 'Monster Beverage Corporation',
    'MAR': 'Marriott International Inc.',
    'MCHP': 'Microchip Technology Inc.',
    'ABNB': 'Airbnb Inc.',
    'ADSK': 'Autodesk Inc.',
    'IDXX': 'IDEXX Laboratories Inc.',
    'BIIB': 'Biogen Inc.',
    'DXCM': 'DexCom Inc.',
    'EXC': 'Exelon Corporation',
    'CHTR': 'Charter Communications Inc.',
    'WBD': 'Warner Bros. Discovery Inc.',
    'ZM': 'Zoom Video Communications Inc.',
    'TEAM': 'Atlassian Corporation Plc',
    'ROST': 'Ross Stores Inc.',
    'ODFL': 'Old Dominion Freight Line Inc.',
    'VRSK': 'Verisk Analytics Inc.',
    'CPRT': 'Copart Inc.',
    'BKR': 'Baker Hughes Company',
    'CTAS': 'Cintas Corporation',
    'PAYX': 'Paychex Inc.',
    'PCAR': 'PACCAR Inc',
    'EA': 'Electronic Arts Inc.',
    'GFS': 'GLOBALFOUNDRIES Inc.',
    'SIRI': 'Sirius XM Holdings Inc.',
    'DLTR': 'Dollar Tree Inc.',
    'ILMN': 'Illumina Inc.',
    'JD': 'JD.com Inc.',
    'KHC': 'The Kraft Heinz Company',
    'MRNA': 'Moderna Inc.',
    'FANG': 'Diamondback Energy Inc.',
    'XEL': 'Xcel Energy Inc.',
    'EBAY': 'eBay Inc.',
    'FAST': 'Fastenal Company',
    'CRWD': 'CrowdStrike Holdings Inc.',
    'ANSS': 'ANSYS Inc.',
    'ASML': 'ASML Holding N.V.',
    'AEP': 'American Electric Power Company Inc.',
    'WDAY': 'Workday Inc.',
    'CTSH': 'Cognizant Technology Solutions Corporation',
    'CEG': 'Constellation Energy Corporation',
    'DDOG': 'Datadog Inc.',
    'WBA': 'Walgreens Boots Alliance Inc.',
    'LCID': 'Lucid Group Inc.',
    'RIVN': 'Rivian Automotive Inc.',
    'ZS': 'Zscaler Inc.',
    'ENPH': 'Enphase Energy Inc.',
    'ALGN': 'Align Technology Inc.',
    'GEHC': 'GE HealthCare Technologies Inc.',
    'ON': 'ON Semiconductor Corporation',
    'TTD': 'The Trade Desk Inc.',
    'VTRS': 'Viatris Inc.',
    'RYAAY': 'Ryanair Holdings plc',
    'POOL': 'Pool Corporation',
    'BIDU': 'Baidu Inc.',
    'PDD': 'PDD Holdings Inc.'
}

# Filter companies based on search
if search:
    filtered_companies = {k: v for k, v in nasdaq100.items() 
                        if search.upper() in k or search.lower() in v.lower()}
else:
    filtered_companies = nasdaq100

# Create a more responsive table layout
for symbol, company in filtered_companies.items():
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        st.write(f"**{symbol}**")
    with col2:
        st.write(company)
    with col3:
        if symbol not in st.session_state.tickers:
            if st.button("Add", key=f"add_{symbol}", use_container_width=True):
                st.session_state.tickers.append(symbol)
                st.session_state.weights = {t: 1/len(st.session_state.tickers) 
                                          for t in st.session_state.tickers}
                st.rerun()
        else:
            st.write("✓ Added")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    Built with Streamlit, yfinance, and QuantStats<br>
    <small>Created by <a href='https://lennartandreasgursky.netlify.app/' target='_blank'>Lennart Andreas Gursky</a></small>
</div>
""", unsafe_allow_html=True) 