# src/processing/weighter.py
"""
Calculate portfolio weights for each holding in a filing.
Weight = (holding value / total portfolio value) * 100
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import Filing, Holding

def calculate_weights_for_filing(filing_id):
    """
    Calculate weight percentages for all holdings in a filing.
    
    Args:
        filing_id: The ID of the filing to calculate weights for
    """
    session = get_session()
    
    # Get the filing
    filing = session.query(Filing).filter_by(id=filing_id).first()
    if not filing:
        print(f"Filing {filing_id} not found")
        return
    
    if filing.total_value == 0:
        print(f"Filing {filing_id} has zero total value, skipping")
        return
    
    # Get all holdings for this filing
    holdings = session.query(Holding).filter_by(filing_id=filing_id).all()
    
    print(f"Calculating weights for filing {filing_id} ({len(holdings)} holdings)...")
    
    # Calculate and update weights
    for holding in holdings:
        if holding.value > 0:
            holding.weight_pct = (holding.value / filing.total_value) * 100
    
    session.commit()
    print(f"✓ Updated weights for {len(holdings)} holdings")

def calculate_weights_for_all_filings():
    """Calculate weights for all filings in the database."""
    session = get_session()
    
    filings = session.query(Filing).all()
    print(f"Calculating weights for {len(filings)} filings...")
    
    for filing in filings:
        calculate_weights_for_filing(filing.id)
    
    print("✓ All weights calculated")

if __name__ == "__main__":
    calculate_weights_for_all_filings()