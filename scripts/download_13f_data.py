# scripts/download_13f_data.py
"""
Download 13F filings using piboufilings library.
"""

from piboufilings import get_filings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USER_AGENT_EMAIL, MANAGERS

def download_13f_filings():
    """Download recent 13F filings for tracked funds."""
    
    for fund_name, cik in MANAGERS.items():
        print(f"\n{'='*50}")
        print(f"Downloading {fund_name} (CIK: {cik})")
        print(f"{'='*50}")
        
        try:
            get_filings(
                user_name="Smart Money 13F Tracker",
                user_agent_email=USER_AGENT_EMAIL,
                cik=cik,
                form_type=["13F-HR"],
                start_year=2024,
                end_year=2025,
                base_dir="./data/parsed",
                raw_data_dir="./data/raw",
                keep_raw_files=True,
                max_workers=3
            )
            print(f"✓ Downloaded {fund_name}")
        except Exception as e:
            print(f"✗ Error downloading {fund_name}: {e}")

if __name__ == "__main__":
    download_13f_filings()
    print("\n✓ All 13F data downloaded!")