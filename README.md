# Smart Money 13F Tracker

A tool to track institutional fund managers' stock positions by analyzing SEC 13F-HR filings.

## Features

- **Real-time 13F Data**: Scrape directly from SEC EDGAR
- **Top Holdings**: Color-coded visualization of top 10 positions with position weights
- **Quarterly Delta**: Track what smart money is buying/selling each quarter
- **Sector Analysis**: See sector allocations and trends
- **Multi-Fund Tracking**: Compare positions across different fund managers

## Project Structure

```
smart-money-13f/
├── src/
│   ├── sec_crawler.py       # SEC EDGAR API scraping
│   ├── data_processor.py    # Calculate deltas, sectors, etc.
│   ├── models.py            # Data models/schemas
│   └── utils.py             # Helper utilities
├── app/
│   └── streamlit_app.py     # Main Streamlit interface
├── data/                    # Cache for downloaded data
└── notebooks/               # Exploratory analysis
```

## Setup

1. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**:
   ```bash
   streamlit run app/streamlit_app.py
   ```

## Development Roadmap

### Phase 1: SEC Data Pipeline
- [ ] Build SEC EDGAR crawler for 13F-HR filings
- [ ] Parse XML filings to extract holdings
- [ ] Store data locally for caching

### Phase 2: Core Analysis
- [ ] Calculate quarterly deltas (buy/sell/hold)
- [ ] Add sector classification
- [ ] Implement position weighting

### Phase 3: Streamlit Dashboard
- [ ] Top 10 holdings visualization
- [ ] Quarterly change tracking
- [ ] Sector heatmap
- [ ] Fund comparison view

### Phase 4: Enhancements
- [ ] Multi-fund aggregation (see what smart money collectively is buying)
- [ ] Historical trend analysis
- [ ] Export to CSV/PDF

## Key Fund Managers to Track

Start with portfolios like:
- AKO Capital
- Berkowitz Fund  
- Christopher Davis
- Third Point Partners
- Tiger Global

See SEC EDGAR for their CIK numbers: https://www.sec.gov/cgi-bin/browse-edgar

## API Reference

**SEC EDGAR**: https://www.sec.gov/cgi-bin/browse-edgar
- Search funds by CIK
- Download 13F-HR filings (XML format)
- Free, no API key needed

## Notes

- 13F filings are required quarterly for managers with >$100M in US equities
- Data is public and 45 days delayed
- Focus on large positions to see real portfolio conviction

