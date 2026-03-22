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
    get_managers, get_filings_for_manager, get_top_holdings, get_qoq_changes, get_buy_history, get_sell_history, get_quarterly_changes_formatted
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
tab1, tab2, tab3, tab4 = st.tabs(["Top Holdings", "Quarterly Changes", "Buys", "Sells"])

with tab1:
    st.subheader(f"Top 10 Holdings - {fund_name}")
    holdings = get_top_holdings(fund_name, selected_date, limit=10)
    
    if holdings:
        df = pd.DataFrame(holdings)
        df['value'] = df['value'].apply(lambda x: f"${x:,}")
        df.index = range(1, len(df) + 1)
        st.dataframe(df, width='stretch')
        
        # Chart: Top holdings by value
        holdings_chart = pd.DataFrame(holdings)
        fig = px.bar(
            holdings_chart,
            x='company_name',
            y='value',
            title=f"Top 10 Holdings - {selected_date}",
            labels={'company_name': 'Company', 'value': 'Value ($1000s)'}
        )
        st.plotly_chart(fig, use_container_width=True, key="top_holdings_chart")
    else:
        st.info(f"No holdings data available for {selected_date}")

with tab2:
    st.subheader(f"Quarter-over-Quarter Change - {fund_name}")
    
    qoq_activity = get_quarterly_changes_formatted(fund_name)
    
    if qoq_activity:
        df = pd.DataFrame(qoq_activity)
        
        # Get unique quarters (should be just one or two for QoQ, but handle multiple)
        quarter_order = {f"Q{i} {y}": i + (y-2000)*4 for y in range(2000, 2100) for i in range(1, 5)}
        df['sort_key'] = df['quarter'].map(quarter_order)
        df = df.sort_values('sort_key', ascending=False).drop('sort_key', axis=1)
        
        quarters = df['quarter'].unique()
        
        # Display each quarter in a separate table
        for quarter in quarters:
            quarter_df = df[df['quarter'] == quarter].copy()
            
            # Prepare display dataframe
            display_df = quarter_df[['stock', 'activity', 'share_change', 'portfolio_weight_change']].copy()
            display_df.columns = ['Stock', 'Activity', 'Share change', '% change to portfolio']
            
            # Format share_change with commas
            display_df['Share change'] = display_df['Share change'].apply(lambda x: f"{x:,}")
            
            # Format percentage
            display_df['% change to portfolio'] = display_df['% change to portfolio'].apply(lambda x: f"{x:.2f}")
            
            # Define color function for different activity types
            def highlight_activity(val):
                if val == 'Buy' or val.startswith('Add'):
                    return 'color: #4ade80; font-weight: bold'  # Green for buys/adds
                elif val == 'Sell 100%' or val.startswith('Reduce'):
                    return 'color: #ef4444; font-weight: bold'  # Red for sells/reduces
                return ''
            
            # Display subheader with quarter
            st.subheader(quarter)
            
            # Style and display the dataframe
            styled_df = display_df.style.applymap(highlight_activity, subset=['Activity'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No quarterly changes available.")

with tab3:
    st.subheader(f"Buy History - {fund_name}")
    
    buy_activity = get_buy_history(fund_name, limit_quarters=8)
    
    if buy_activity:
        # Group by quarter for display
        df = pd.DataFrame(buy_activity)
        
        # Sort by quarter (newest first)
        quarter_order = {f"Q{i} {y}": i + (y-2000)*4 for y in range(2000, 2100) for i in range(1, 5)}
        df['sort_key'] = df['quarter'].map(quarter_order)
        df = df.sort_values('sort_key', ascending=False).drop('sort_key', axis=1)
        
        # Get unique quarters
        quarters = df['quarter'].unique()
        
        # Display each quarter in a separate table
        for quarter in quarters:
            quarter_df = df[df['quarter'] == quarter].copy()
            
            # Prepare display dataframe
            display_df = quarter_df[['stock', 'activity', 'share_change', 'portfolio_weight_change']].copy()
            display_df.columns = ['Stock', 'Activity', 'Share change', '% change to portfolio']
            
            # Format share_change with commas
            display_df['Share change'] = display_df['Share change'].apply(lambda x: f"{x:,}")
            
            # Format percentage
            display_df['% change to portfolio'] = display_df['% change to portfolio'].apply(lambda x: f"{x:.2f}")
            
            # Define color function for styling
            def highlight_buy(val):
                if val == 'Buy' or val.startswith('Add'):
                    return 'color: #4ade80; font-weight: bold'
                return ''
            
            # Display subheader with quarter
            st.subheader(quarter)
            
            # Style and display the dataframe
            styled_df = display_df.style.applymap(highlight_buy, subset=['Activity'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No buy activity data available.")

with tab4:
    st.subheader(f"Sell History - {fund_name}")
    
    sell_activity = get_sell_history(fund_name, limit_quarters=8)
    
    if sell_activity:
        # Group by quarter for display
        df = pd.DataFrame(sell_activity)
        
        # Sort by quarter (newest first)
        quarter_order = {f"Q{i} {y}": i + (y-2000)*4 for y in range(2000, 2100) for i in range(1, 5)}
        df['sort_key'] = df['quarter'].map(quarter_order)
        df = df.sort_values('sort_key', ascending=False).drop('sort_key', axis=1)
        
        # Get unique quarters
        quarters = df['quarter'].unique()
        
        # Display each quarter in a separate table
        for quarter in quarters:
            quarter_df = df[df['quarter'] == quarter].copy()
            
            # Prepare display dataframe
            display_df = quarter_df[['stock', 'activity', 'share_change', 'portfolio_weight_change']].copy()
            display_df.columns = ['Stock', 'Activity', 'Share change', '% change to portfolio']
            
            # Format share_change with commas
            display_df['Share change'] = display_df['Share change'].apply(lambda x: f"{x:,}")
            
            # Format percentage
            display_df['% change to portfolio'] = display_df['% change to portfolio'].apply(lambda x: f"{x:.2f}")
            
            # Define color function for styling (red for sells)
            def highlight_sell(val):
                if val == 'Sell 100%' or val.startswith('Reduce'):
                    return 'color: #ef4444; font-weight: bold'
                return ''
            
            # Display subheader with quarter
            st.subheader(quarter)
            
            # Style and display the dataframe
            styled_df = display_df.style.applymap(highlight_sell, subset=['Activity'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.info("No sell activity data available.")
