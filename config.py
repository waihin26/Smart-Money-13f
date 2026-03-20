# config.py
import os

# Database
DB_PATH = "data/smart_money.db"

# SEC API settings
SEC_SUBMISSIONS_API = "https://data.sec.gov/submissions/CIK{}.json"
REQUESTS_PER_SECOND = 5
USER_AGENT_EMAIL = "wongwaihin7@gmail.com"  

# Fund managers that file 13F-HR (verified CIKs)
MANAGERS = {
    "Berkshire Hathaway": "0001018724",
    "Soros Fund Management": "0001029160",
}

# Create directories if they don't exist
os.makedirs("data/raw/filings", exist_ok=True)
os.makedirs("data/parsed", exist_ok=True)