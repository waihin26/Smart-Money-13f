"""
Main Streamlit app for Smart Money 13F Tracker.
Visualizes SEC 13F filings for fund managers.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from src.analytics.portfolio_analytics import (
    get_managers, get_filings_for_manager, get_top_holdings, get_qoq_changes
)

st.set_page_config(page_title="Smart Money 13F Tracker", layout="wide")

st.title("Smart Money 13F Tracker")
st.markdown("""
Track what institutional fund managers are buying.
Analyze quarterly 13F-HR SEC filings from top asset managers.
""")

# Sidebar for fund selection
st.sidebar.header("Filter Options")

# Get managers from database
managers = get_managers()

if not managers:
    st.error("No managers found in database. Please run: python scripts/load_13f_to_db.py")
    st.stop()

fund_name = st.sidebar.selectbox("Select Fund Manager", managers)

# Get available filings for this manager
filings = get_filings_for_manager(fund_name)

if not filings:
    st.error(f"No filings found for {fund_name}")
    st.stop()

# Extract filing dates
filing_dates = [f[1] for f in filings]  # f[1] is the date string
selected_date = st.sidebar.selectbox("Select Filing Period", filing_dates)

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Top Holdings", "Quarterly Changes", "Sector Analysis"])

with tab1:
    st.subheader(f"Top 10 Holdings - {fund_name}")
    holdings = get_top_holdings(fund_name, selected_date, limit=10)
    
    if holdings:
        df = pd.DataFrame(holdings)
        df['value'] = df['value'].apply(lambda x: f"${x:,}")
        st.dataframe(df, use_container_width=True)
        
        # Chart: Top holdings by value
        holdings_chart = pd.DataFrame(holdings)
        fig = px.bar(
            holdings_chart,
            x='company_name',
            y='value',
            title=f"Top 10 Holdings - {selected_date}",
            labels={'company_name': 'Company', 'value': 'Value ($1000s)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"No holdings data available for {selected_date}")

with tab2:
    st.subheader("What's Changing? (Quarter-over-Quarter)")
    qoq = get_qoq_changes(fund_name)
    
    if 'message' in qoq:
        st.info(qoq['message'])
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**New Positions**")
            if qoq.get('NEW'):
                new_df = pd.DataFrame(qoq['NEW'])
                st.dataframe(new_df, use_container_width=True)
            else:
                st.write("No new positions")
        
        with col2:
            st.write("**Increased Positions**")
            if qoq.get('INCREASED'):
                inc_df = pd.DataFrame(qoq['INCREASED'])
                st.dataframe(inc_df, use_container_width=True)
            else:
                st.write("No increased positions")

with tab3:
    st.subheader("Sector Breakdown")
    st.info("Sector analysis coming soon")
