"""
Main Streamlit app for Smart Money 13F Tracker.
Visualizes SEC 13F filings for fund managers.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Smart Money 13F Tracker", layout="wide")

st.title("Smart Money 13F Tracker")
st.markdown("""
Track what institutional fund managers are buying.
Analyze quarterly 13F-HR SEC filings from top asset managers.
""")

# Sidebar for fund selection
st.sidebar.header("Filter Options")
fund_name = st.sidebar.selectbox(
    "Select Fund Manager",
    ["AKO Capital", "Berkowitz Fund", "Third Point Partners", "Tiger Global"]
)

quarter = st.sidebar.selectbox(
    "Select Quarter",
    ["Q4 2025", "Q3 2025", "Q2 2025", "Q1 2025"]
)

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Top Holdings", "Quarterly Changes", "Sector Analysis"])

with tab1:
    st.subheader(f"Top 10 Holdings - {fund_name}")
    # TODO: Load and display top 10 holdings
    st.info("Connect SEC crawler to display holdings data")

with tab2:
    st.subheader("What's Changing? (Quarter-over-Quarter)")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**New Positions**")
        # TODO: Display new positions
    with col2:
        st.write("**Increased Positions**")
        # TODO: Display increased positions

with tab3:
    st.subheader("Sector Breakdown")
    # TODO: Display sector allocation
    st.info("Sector analysis coming soon")
