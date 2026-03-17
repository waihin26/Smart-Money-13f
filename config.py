# config.py
import os

# Database
DB_PATH = "data/smart_money.db"

# SEC API settings
SEC_SUBMISSIONS_API = "https://data.sec.gov/submissions/CIK{}.json"
REQUESTS_PER_SECOND = 5

# Managers to track (CIK = SEC identifier for each manager)
MANAGERS = {
    "AKO Capital": "1337637",
    "Berkowitz Fund": "1082838",
    "Christopher Davis": "1322841",
    "Third Point Partners": "1384978",
}

# Create directories if they don't exist
os.makedirs("data/raw/filings", exist_ok=True)