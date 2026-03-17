# database/models.py
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Manager(Base):
    """Fund manager (e.g., AKO Capital, Berkowitz Fund)"""
    __tablename__ = 'managers'
    
    cik = Column(String, primary_key=True)           # "1337637"
    name = Column(String, unique=True)               # "AKO Capital"
    aum_millions = Column(Float, nullable=True)      # Assets under management
    last_updated = Column(DateTime, default=datetime.utcnow)


class Filing(Base):
    """A single 13F-HR quarterly filing"""
    __tablename__ = 'filings'
    
    id = Column(Integer, primary_key=True)
    manager_cik = Column(String, ForeignKey('managers.cik'))
    accession_number = Column(String, unique=True)   # Unique filing ID
    filing_date = Column(Date)                        # When filed with SEC
    period_of_report = Column(Date)                   # Quarter-end date
    total_value = Column(Integer)                     # Portfolio value (in thousands)
    created_at = Column(DateTime, default=datetime.utcnow)


class Holding(Base):
    """A single stock holding in a filing"""
    __tablename__ = 'holdings'
    
    id = Column(Integer, primary_key=True)
    filing_id = Column(Integer, ForeignKey('filings.id'))
    
    # Stock identifiers
    cusip = Column(String)                           # Stock ID code
    ticker = Column(String, nullable=True)           # "AAPL", "MSFT", etc
    company_name = Column(String)
    
    # Position data
    shares = Column(Integer)                         # How many shares
    value = Column(Integer)                          # Portfolio value (in thousands)
    weight_pct = Column(Float, nullable=True)        # Percentage of portfolio