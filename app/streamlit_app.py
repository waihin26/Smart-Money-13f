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
    get_managers, get_filings_for_manager, get_top_holdings, get_qoq_changes, get_buy_history, get_sell_history, get_quarterly_changes_formatted, get_all_managers_with_holdings
)

st.set_page_config(page_title="Smart Money 13F Tracker", layout="wide")

st.title("Smart Money 13F Tracker")
st.markdown("""
Track what institutional fund managers are buying.
Analyze quarterly 13F-HR SEC filings from top asset managers.
""")

# Get managers from database
managers = get_managers()

if not managers:
    st.error("No managers found in database. Please run: python scripts/load_13f_to_db.py")
    st.stop()

# Main tabs
tab_home, tab1, tab2, tab3, tab4 = st.tabs(["Home", "Top Holdings", "Quarterly Changes", "Buys", "Sells"])

# ===== HOME TAB =====
with tab_home:
    st.subheader("Smart Money Funds Overview")
    
    # Get all managers' data
    all_managers_data = get_all_managers_with_holdings()
    
    if all_managers_data:
        # Display funds in horizontal cards
        for manager_data in all_managers_data:
            with st.container():
                # Create columns for layout
                col_name, col_value, col_holdings = st.columns([1.5, 1, 2.5])
                
                with col_name:
                    st.markdown(f"### {manager_data['name']}")
                
                with col_value:
                    st.markdown("**Portfolio Value**")
                    if manager_data['portfolio_value'] >= 1000000:
                        value_str = f"${manager_data['portfolio_value'] / 1000000:.1f}B"
                    else:
                        value_str = f"${manager_data['portfolio_value'] / 1000:.1f}M"
                    st.metric("", value_str)
                
                with col_holdings:
                    st.markdown(f"**Top 10 Holdings** ({manager_data['num_stocks']} positions)")
                    holdings_list = " • ".join([h['company_name'] for h in manager_data['top_holdings']])
                    st.caption(holdings_list)
                
                st.divider()
    else:
        st.info("No fund data available")

# Sidebar for fund selection for detail tabs
st.sidebar.header("Fund Details")
selected_fund = st.sidebar.selectbox("Select Fund Manager", managers, key="fund_selector")

# Get available filings for selected manager
filings = get_filings_for_manager(selected_fund)

if not filings:
    st.error(f"No filings found for {selected_fund}")
    st.stop()

# Extract filing dates
filing_dates = [f[1] for f in filings]
selected_date = st.sidebar.selectbox("Select Filing Period", filing_dates)

# ===== TOP HOLDINGS TAB =====
with tab1:
    st.subheader(f"Top 10 Holdings - {selected_fund}")
    holdings = get_top_holdings(selected_fund, selected_date, limit=10)
    
    if holdings:
        df = pd.DataFrame(holdings)
        df['value'] = df['value'].apply(lambda x: f"${x:,}")
        df.index = range(1, len(df) + 1)
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
        st.plotly_chart(fig, use_container_width=True, key="top_holdings_chart")
    else:
        st.info(f"No holdings data available for {selected_date}")

# ===== QUARTERLY CHANGES TAB =====
with tab2:
    st.subheader(f"Quarter-over-Quarter Change - {selected_fund}")
    
    qoq_activity = get_quarterly_changes_formatted(selected_fund)
    
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

# ===== BUYS TAB =====
with tab3:
    st.subheader(f"Buy History - {selected_fund}")
    
    buy_activity = get_buy_history(selected_fund, limit_quarters=8)
    
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

# ===== SELLS TAB =====
with tab4:
    st.subheader(f"Sell History - {selected_fund}")
    
    sell_activity = get_sell_history(selected_fund, limit_quarters=8)
    
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
