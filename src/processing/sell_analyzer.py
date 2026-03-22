"""
Analyze sell activity across quarterly filings.
Identifies exited positions (SELL 100%) and reduced positions (REDUCE x%).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import Manager, Filing, Holding
from sqlalchemy import desc
from datetime import datetime


def get_sell_activity(manager_name, limit_quarters=None):
    """
    Get sell activity organized by quarter and stock.
    
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
            'activity': 'Sell 100%',  # or 'Reduce 25.3%'
            'share_change': 1000000,
            'previous_shares': 1000000,
            'current_shares': 0 (for exits), or X (for reductions)
            'share_value': 50000,  # value in thousands (recent value)
            'portfolio_weight_change': -2.5,  # percentage (negative)
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
        previous_portfolio_value = max(previous_portfolio_value, 1)
        
        # Find REDUCED and EXITED positions
        for company_name, previous_holding in previous_map.items():
            if company_name not in recent_map:
                # EXITED POSITION (completely sold)
                activity_type = "Sell 100%"
                share_change = previous_holding.shares
                current_shares = 0
                weight_change = -(previous_holding.value / previous_portfolio_value) * 100
                share_value = previous_holding.value  # Use previous value since it's no longer held
            else:
                # Existing position
                recent_holding = recent_map[company_name]
                if recent_holding.shares < previous_holding.shares:
                    # REDUCED POSITION
                    share_change = previous_holding.shares - recent_holding.shares
                    current_shares = recent_holding.shares
                    previous_weight = (previous_holding.value / previous_portfolio_value) * 100
                    recent_weight = (recent_holding.value / recent_portfolio_value) * 100
                    weight_change = recent_weight - previous_weight  # This will be negative
                    
                    # Calculate percentage reduction
                    pct_reduction = ((previous_holding.shares - recent_holding.shares) / previous_holding.shares) * 100
                    activity_type = f"Reduce {pct_reduction:.1f}%"
                    share_value = recent_holding.value
                else:
                    # Increased or unchanged - skip
                    continue
            
            # Format quarter as "Q1 2025", "Q2 2025", etc.
            quarter_num = (recent_filing.period_of_report.month - 1) // 3 + 1
            quarter_str = f"Q{quarter_num} {recent_filing.period_of_report.year}"
            
            activity_list.append({
                'quarter': quarter_str,
                'period_date': recent_filing.period_of_report.strftime('%Y-%m-%d'),
                'stock': company_name,
                'company_name': company_name,
                'ticker': previous_holding.ticker,
                'activity': activity_type,
                'share_change': share_change,
                'previous_shares': previous_holding.shares,
                'current_shares': current_shares,
                'share_value': share_value,
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


def get_sell_activity_by_quarter(manager_name, quarter_str):
    """
    Get sell activity for a specific quarter.
    
    Args:
        manager_name: Fund manager name
        quarter_str: Quarter string like "Q1 2025"
    
    Returns:
        List of activity dicts for that quarter, sorted by share value (descending)
    """
    all_activity = get_sell_activity(manager_name)
    
    quarter_activity = [a for a in all_activity if a['quarter'] == quarter_str]
    
    # Sort by value (descending)
    quarter_activity.sort(key=lambda x: x['share_value'], reverse=True)
    
    return quarter_activity
