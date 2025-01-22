import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize session state for shared variables
if 'tickers' not in st.session_state:
    st.session_state.tickers = ["AAPL", "MSFT", "GOOGL", "NVDA"]

# When initializing or recalculating weights
def calculate_balanced_weights(tickers):
    num_tickers = len(tickers)
    base_weight = 100 // num_tickers  # Integer division
    remainder = 100 - (base_weight * num_tickers)  # This will be 4 for 6 tickers
    
    weights = {}
    for i, ticker in enumerate(tickers):
        # Distribute remainder one by one until it's all used up
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
    weights[ticker] = weight / 100  # Store as decimal (0.17 instead of 17)

# Update session state weights all at once after the loop
st.session_state.weights = weights

# Add a running total display
st.sidebar.markdown(f"**Total Portfolio Weight: {total_weight}%**")
if total_weight != 100:
    st.sidebar.warning("⚠️ Total weight should equal 100%")

# Main content
st.title("📈 Stock Analysis Dashboard")
st.write("Welcome to the Stock Analysis Dashboard! Configure your portfolio settings in the sidebar.")

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

st.markdown("""
### Available Analysis Pages:
1. **Technical Analysis**: View candlestick charts, moving averages, and other technical indicators
2. **Portfolio Analysis**: Analyze portfolio returns and correlation between assets
3. **Risk Metrics**: Detailed risk analysis using QuantStats
""")

# Nasdaq 100 Companies section
st.markdown("### Nasdaq 100 Companies")
search = st.text_input("Search companies", "")

# Define Nasdaq 100 companies (you might want to fetch this data dynamically)
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

# Create a DataFrame for display
df_companies = pd.DataFrame({
    'Symbol': filtered_companies.keys(),
    'Company': filtered_companies.values()
}).reset_index(drop=True)

# Use a smaller container width and shift left
left_col, center_col, _ = st.columns([0.1, 1, 1])  # Adjusted ratio to shift content left
with center_col:
    for idx, row in df_companies.iterrows():
        col1, col2, col3 = st.columns([0.2, 2, 0.2])
        with col1:
            st.write(row['Symbol'])
        with col2:
            st.write(row['Company'])
        with col3:
            if st.button("Add", key=f"add_{row['Symbol']}", use_container_width=True):
                if row['Symbol'] not in st.session_state.tickers:
                    st.session_state.tickers.append(row['Symbol'])
                    st.session_state.weights = {t: 1/len(st.session_state.tickers) 
                                              for t in st.session_state.tickers}
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("Built with Streamlit, yfinance, and QuantStats") 