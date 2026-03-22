"""
Analyze buy activity across quarterly filings.
Identifies new positions (BUY) and increased positions (ADD x%).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import Manager, Filing, Holding
from sqlalchemy import desc
from datetime import datetime


def get_buy_activity(manager_name, limit_quarters=None):
    """
    Get buy activity organized by quarter and stock.
    
    Args:
        manager_name: Fund manager name
        limit_quarters: Limit to N most recent quarters (None = all)
    
    Returns:
        List of dicts with: {
            'quarter': 'Q4 2025',
            'period_date': '2025-12-31',
            'stock': 'AAPL',
            'company_name': 'Apple Inc.',
            'ticker': 'AAPL',
            'activity': 'Buy',  # or 'Add 25.3%'
            'share_change': 1000000,
            'previous_shares': 0 (for new), or X (for increases)
            'current_shares': 1000000,
            'share_value': 50000,  # value in thousands
            'portfolio_weight_change': 2.5,  # percentage
        }
    """
    session = get_session()
    
    manager = session.query(Manager).filter_by(name=manager_name).first()
    if not manager:
        return []
    
    # Get all filings for this manager, sorted by date (newest first)
    filings = session.query(Filing).filter_by(manager_cik=manager.cik).order_by(
        desc(Filing.period_of_report)
    ).all()
    
    if len(filings) < 2:
        return []
    
    activity_list = []
    
    # Compare each filing with the previous one
    for i in range(len(filings) - 1):
        recent_filing = filings[i]
        previous_filing = filings[i + 1]
        
        # Get all holdings from both filings
        recent_holdings = session.query(Holding).filter_by(filing_id=recent_filing.id).all()
        previous_holdings = session.query(Holding).filter_by(filing_id=previous_filing.id).all()
        
        # Create maps: company_name -> Holding object
        recent_map = {h.company_name: h for h in recent_holdings}
        previous_map = {h.company_name: h for h in previous_holdings}
        
        # Calculate portfolio value for weight calculations
        recent_portfolio_value = sum(h.value for h in recent_holdings)
        previous_portfolio_value = sum(h.value for h in previous_holdings)
        recent_portfolio_value = max(recent_portfolio_value, 1)
        
        # Find NEW positions and INCREASED positions
        for company_name, recent_holding in recent_map.items():
            if company_name not in previous_map:
                # NEW POSITION
                activity_type = "Buy"
                share_change = recent_holding.shares
                previous_shares = 0
                weight_change = (recent_holding.value / recent_portfolio_value) * 100
            else:
                # Existing position
                previous_holding = previous_map[company_name]
                if recent_holding.shares > previous_holding.shares:
                    # INCREASED POSITION
                    share_change = recent_holding.shares - previous_holding.shares
                    previous_shares = previous_holding.shares
                    previous_weight = (previous_holding.value / previous_portfolio_value) * 100
                    recent_weight = (recent_holding.value / recent_portfolio_value) * 100
                    weight_change = recent_weight - previous_weight
                    
                    # Calculate percentage increase
                    pct_increase = ((recent_holding.shares - previous_holding.shares) / previous_holding.shares) * 100
                    activity_type = f"Add {pct_increase:.1f}%"
                else:
                    # Decreased or unchanged - skip
                    continue
            
            # Format quarter as "Q1 2025", "Q2 2025", etc.
            quarter_num = (recent_filing.period_of_report.month - 1) // 3 + 1
            quarter_str = f"Q{quarter_num} {recent_filing.period_of_report.year}"
            
            activity_list.append({
                'quarter': quarter_str,
                'period_date': recent_filing.period_of_report.strftime('%Y-%m-%d'),
                'stock': company_name,
                'company_name': company_name,
                'ticker': recent_holding.ticker,
                'activity': activity_type,
                'share_change': share_change,
                'previous_shares': previous_shares,
                'current_shares': recent_holding.shares,
                'share_value': recent_holding.value,
                'portfolio_weight_change': round(weight_change, 2),
            })
    
    # Limit to N quarters if specified
    if limit_quarters:
        quarters_seen = set()
        limited_activity = []
        for item in activity_list:
            if item['quarter'] not in quarters_seen:
                quarters_seen.add(item['quarter'])
                if len(quarters_seen) > limit_quarters:
                    break
            limited_activity.append(item)
        return limited_activity
    
    return activity_list


def get_buy_activity_by_quarter(manager_name, quarter_str):
    """
    Get buy activity for a specific quarter.
    
    Args:
        manager_name: Fund manager name
        quarter_str: Quarter string like "Q1 2025"
    
    Returns:
        List of activity dicts for that quarter, sorted by share value (descending)
    """
    all_activity = get_buy_activity(manager_name)
    
    quarter_activity = [a for a in all_activity if a['quarter'] == quarter_str]
    
    # Sort by value (descending)
    quarter_activity.sort(key=lambda x: x['share_value'], reverse=True)
    
    return quarter_activity
