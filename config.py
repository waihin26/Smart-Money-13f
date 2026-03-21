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
    "Berkshire Hathaway": "0000086768",
    "Soros Fund Management": "0001029160",
    "Point72 Asset Management": "0001603466",
    "Citadel Advisors": "0001423053",
    "Bridgewater Associates": "0001350694",
    "Millennium Management": "0001273087",
    "Tiger Global Management": "0001167483",
    "D.E. Shaw & Co": "0001009268",
    "Pershing Square Capital": "0001336528",
    "AQR CAPITAL MANAGEMENT LLC": "0001167557",
    "TWO SIGMA INVESTMENTS, LP": "0001179392",
    "Elliott Management": "0001791786",
    "Qube Research & Technologies": "0001729829"
}

# Create directories if they don't exist
os.makedirs("data/raw/filings", exist_ok=True)
os.makedirs("data/parsed", exist_ok=True)