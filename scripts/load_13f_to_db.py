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
    
    # Normalize dates in both dataframes (handle mixed format)
    info_df['CONFORMED_DATE'] = pd.to_datetime(info_df['CONFORMED_DATE'], format='mixed').dt.strftime('%Y-%m-%d')
    holdings_df['CONFORMED_DATE'] = pd.to_datetime(holdings_df['CONFORMED_DATE'], format='mixed').dt.strftime('%Y-%m-%d')
    
    # Process each filing
    for idx, row in info_df.iterrows():
        cik = str(int(row['CIK'])).zfill(10)
        manager_name = row['COMPANY_NAME']
        sec_file_number = row['SEC_FILE_NUMBER']
        conformed_date = row['CONFORMED_DATE']
        
        # Extract unique accession number from SEC_FILING_URL
        filing_url = str(row['SEC_FILING_URL'])
        # URL format: https://www.sec.gov/Archives/edgar/data/CIK/XXXXXXXXXX/accession-number.txt
        # Extract accession number from URL
        accession_number = filing_url.split('/')[-1].replace('.txt', '')
        
        print(f"\nProcessing: {manager_name} - {conformed_date} (Accession: {accession_number})")
        
        # Create or get manager
        manager = session.query(Manager).filter_by(cik=cik).first()
        if not manager:
            manager = Manager(cik=cik, name=manager_name)
            session.add(manager)
            session.commit()
            print(f"  ✓ Created manager: {manager_name}")
        
        # Check if filing already exists (using actual accession number)
        filing = session.query(Filing).filter_by(accession_number=accession_number).first()
        if filing:
            print(f"  ℹ Filing {accession_number} already exists, skipping")
            continue
        
        # Create filing record
        filing = Filing(
            manager_cik=cik,
            accession_number=accession_number,
            filing_date=pd.to_datetime(row['FILED_DATE']).date() if pd.notna(row['FILED_DATE']) else None,
            period_of_report=pd.to_datetime(row['CONFORMED_DATE']).date() if pd.notna(row['CONFORMED_DATE']) else None,
            total_value=int(row['TOTAL_VALUE']) if pd.notna(row['TOTAL_VALUE']) else 0
        )
        session.add(filing)
        session.commit()
        print(f"  ✓ Created filing: {accession_number}")
        
        # Add holdings for this filing - match by SEC_FILE_NUMBER and CONFORMED_DATE
        filing_holdings = holdings_df[
            (holdings_df['SEC_FILE_NUMBER'] == sec_file_number) &
            (holdings_df['CONFORMED_DATE'] == conformed_date)
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