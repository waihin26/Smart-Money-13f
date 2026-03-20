# scripts/load_13f_to_db.py
"""
Load downloaded 13F CSV data into the database.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from database.connection import get_session, init_db
from database.models import Manager, Filing, Holding
from datetime import datetime

def load_13f_data():
    """Load 13F CSVs into database."""
    
    # Initialize database
    init_db()
    session = get_session()
    
    # Read CSVs
    print("Reading 13F data files...")
    info_df = pd.read_csv("data/parsed/13f_info.csv")
    holdings_df = pd.read_csv("data/parsed/13f_holdings.csv")
    
    print(f"Found {len(info_df)} filings")
    print(f"Found {len(holdings_df)} holdings")
    
    # Process each filing
    for idx, row in info_df.iterrows():
        cik = str(int(row['CIK'])).zfill(10)
        manager_name = row['COMPANY_NAME']
        sec_file_number = row['SEC_FILE_NUMBER']
        
        print(f"\nProcessing: {manager_name}")
        
        # Create or get manager
        manager = session.query(Manager).filter_by(cik=cik).first()
        if not manager:
            manager = Manager(cik=cik, name=manager_name)
            session.add(manager)
            session.commit()
            print(f"  ✓ Created manager: {manager_name}")
        
        # Check if filing already exists
        filing = session.query(Filing).filter_by(accession_number=sec_file_number).first()
        if filing:
            print(f"  ℹ Filing {sec_file_number} already exists, skipping")
            continue
        
        # Create filing record
        filing = Filing(
            manager_cik=cik,
            accession_number=sec_file_number,
            filing_date=pd.to_datetime(row['FILED_DATE']).date() if pd.notna(row['FILED_DATE']) else None,
            period_of_report=pd.to_datetime(row['CONFORMED_DATE']).date() if pd.notna(row['CONFORMED_DATE']) else None,
            total_value=int(row['TOTAL_VALUE']) if pd.notna(row['TOTAL_VALUE']) else 0
        )
        session.add(filing)
        session.commit()
        print(f"  ✓ Created filing: {sec_file_number}")
        
        # Add holdings for this filing
        filing_holdings = holdings_df[
            holdings_df['SEC_FILE_NUMBER'] == sec_file_number
        ]
        
        count = 0
        for h_idx, h_row in filing_holdings.iterrows():
            try:
                value = int(h_row['SHARE_VALUE']) if pd.notna(h_row['SHARE_VALUE']) else 0
                shares = int(h_row['SHARE_AMOUNT']) if pd.notna(h_row['SHARE_AMOUNT']) else 0
                
                holding = Holding(
                    filing_id=filing.id,
                    cusip=str(h_row['CUSIP']) if pd.notna(h_row['CUSIP']) else '',
                    ticker=None,  # We don't have ticker from piboufilings output
                    company_name=str(h_row['NAME_OF_ISSUER']),
                    shares=shares,
                    value=value,
                )
                session.add(holding)
                count += 1
            except Exception as e:
                print(f"    ✗ Error adding holding: {e}")
        
        session.commit()
        print(f"  ✓ Added {count} holdings")
    
    print("\n✓ All data loaded into database!")

if __name__ == "__main__":
    load_13f_data()