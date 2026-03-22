# scripts/download_13f_data.py
"""
Download 13F filings using piboufilings library.
"""

from piboufilings import get_filings
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USER_AGENT_EMAIL, MANAGERS

def download_13f_filings(start_year=2024, end_year=2025):
    """Download recent 13F filings for tracked funds.
    
    Args:
        start_year: Starting year for filings (default: 2024)
        end_year: Ending year for filings (default: 2025)
    """
    
    # Ensure directories exist
    os.makedirs("./data/parsed", exist_ok=True)
    os.makedirs("./data/raw", exist_ok=True)
    
    success_count = 0
    error_count = 0
    
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
                start_year=start_year,
                end_year=end_year,
                base_dir="./data/parsed",
                raw_data_dir="./data/raw",
                keep_raw_files=True,
                max_workers=3
            )
            print(f"✓ Downloaded {fund_name}")
            success_count += 1
        except Exception as e:
            print(f"✗ Error downloading {fund_name}: {e}")
            error_count += 1
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Download Summary: {success_count} successful, {error_count} errors")
    print(f"{'='*50}")

if __name__ == "__main__":
    download_13f_filings()
    print("\n" + "="*50)
    print("✓ All 13F data downloaded!")
    print("Next: Run 'python scripts/load_13f_to_db.py'")
    print("="*50)