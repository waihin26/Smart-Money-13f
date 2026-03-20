# src/analytics/portfolio_analytics.py
"""
Query and analyze portfolio data for visualization.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_session
from database.models import Manager, Filing, Holding
from sqlalchemy import desc

def get_managers():
    """Get list of all managers in database."""
    session = get_session()
    managers = session.query(Manager).all()
    return [m.name for m in managers]

def get_filings_for_manager(manager_name):
    """Get all filings for a manager, sorted by date."""
    session = get_session()
    manager = session.query(Manager).filter_by(name=manager_name).first()
    if not manager:
        return []
    
    filings = session.query(Filing).filter_by(manager_cik=manager.cik).order_by(
        desc(Filing.period_of_report)
    ).all()
    
    return [(f.id, f.period_of_report.strftime('%Y-%m-%d'), f.total_value) for f in filings]

def get_top_holdings(manager_name, filing_date, limit=10):
    """
    Get top N holdings by value for a manager on a specific date.
    Aggregates by company name to avoid duplicates from different share classes.
    
    Args:
        manager_name: Fund manager name
        filing_date: Filing period date (YYYY-MM-DD)
        limit: Number of top holdings (default 10)
    
    Returns:
        List of dicts with company_name, value, shares, weight_pct
    """
    session = get_session()
    
    manager = session.query(Manager).filter_by(name=manager_name).first()
    if not manager:
        return []
    
    filing = session.query(Filing).filter_by(
        manager_cik=manager.cik,
        period_of_report=filing_date
    ).first()
    
    if not filing:
        return []
    
    holdings = session.query(Holding).filter_by(filing_id=filing.id).all()
    
    # Aggregate by company name (sum values and shares for same company)
    company_totals = {}
    for h in holdings:
        if h.company_name not in company_totals:
            company_totals[h.company_name] = {
                'value': 0,
                'shares': 0
            }
        company_totals[h.company_name]['value'] += h.value
        company_totals[h.company_name]['shares'] += h.shares
    
    # Sort by value and limit
    sorted_companies = sorted(
        company_totals.items(),
        key=lambda x: x[1]['value'],
        reverse=True
    )[:limit]
    
    # Calculate total portfolio value from actual holdings
    total_portfolio_value = sum(data['value'] for data in company_totals.values())
    total_portfolio_value = max(total_portfolio_value, 1)  # Avoid division by zero
    
    return [
        {
            'company_name': name,
            'value': data['value'],
            'shares': data['shares'],
            'weight_pct': round((data['value'] / total_portfolio_value) * 100, 2)
        }
        for name, data in sorted_companies
    ]

def get_portfolio_breakdown(manager_name, filing_date):
    """
    Get all holdings for a manager on a specific date, sorted by weight.
    
    Args:
        manager_name: Fund manager name
        filing_date: Filing period date (YYYY-MM-DD)
    
    Returns:
        List of dicts with company_name, value, weight_pct, shares
    """
    session = get_session()
    
    manager = session.query(Manager).filter_by(name=manager_name).first()
    if not manager:
        return []
    
    filing = session.query(Filing).filter_by(
        manager_cik=manager.cik,
        period_of_report=filing_date
    ).first()
    
    if not filing:
        return []
    
    holdings = session.query(Holding).filter_by(filing_id=filing.id).all()
    
    # Aggregate by company name
    company_totals = {}
    for h in holdings:
        if h.company_name not in company_totals:
            company_totals[h.company_name] = {
                'value': 0,
                'shares': 0
            }
        company_totals[h.company_name]['value'] += h.value
        company_totals[h.company_name]['shares'] += h.shares
    
    # Calculate total portfolio value
    total_portfolio_value = sum(data['value'] for data in company_totals.values())
    total_portfolio_value = max(total_portfolio_value, 1)
    
    # Sort by value descending
    sorted_companies = sorted(
        company_totals.items(),
        key=lambda x: x[1]['value'],
        reverse=True
    )
    
    return [
        {
            'company_name': name,
            'value': data['value'],
            'weight_pct': round((data['value'] / total_portfolio_value) * 100, 2),
            'shares': data['shares']
        }
        for name, data in sorted_companies
    ]

def get_qoq_changes(manager_name):
    """
    Compare positions between the most recent two filings.
    Mark as NEW, INCREASED, DECREASED, or EXITED.
    
    Args:
        manager_name: Fund manager name
    
    Returns:
        Dict with lists of positions by action type
    """
    session = get_session()
    
    manager = session.query(Manager).filter_by(name=manager_name).first()
    if not manager:
        return {}
    
    # Get two most recent filings
    filings = session.query(Filing).filter_by(manager_cik=manager.cik).order_by(
        desc(Filing.period_of_report)
    ).limit(2).all()
    
    if len(filings) < 2:
        return {'message': 'Need at least 2 filings for comparison'}
    
    recent_filing = filings[0]
    previous_filing = filings[1]
    
    # Get holdings from both filings
    recent_holdings = session.query(Holding).filter_by(filing_id=recent_filing.id).all()
    previous_holdings = session.query(Holding).filter_by(filing_id=previous_filing.id).all()
    
    # Create maps of company_name -> value
    recent_map = {h.company_name: h.value for h in recent_holdings}
    previous_map = {h.company_name: h.value for h in previous_holdings}
    
    changes = {
        'NEW': [],
        'INCREASED': [],
        'DECREASED': [],
        'EXITED': []
    }
    
    # Find new and changed positions
    for company, recent_value in recent_map.items():
        if company not in previous_map:
            changes['NEW'].append({
                'company_name': company,
                'value': recent_value,
                'change_pct': 0
            })
        else:
            previous_value = previous_map[company]
            if recent_value > previous_value:
                change_pct = ((recent_value - previous_value) / previous_value) * 100
                changes['INCREASED'].append({
                    'company_name': company,
                    'value': recent_value,
                    'change_pct': round(change_pct, 1)
                })
            elif recent_value < previous_value:
                change_pct = ((previous_value - recent_value) / previous_value) * 100
                changes['DECREASED'].append({
                    'company_name': company,
                    'value': recent_value,
                    'change_pct': round(change_pct, 1)
                })
    
    # Find exited positions
    for company, previous_value in previous_map.items():
        if company not in recent_map:
            changes['EXITED'].append({
                'company_name': company,
                'previous_value': previous_value
            })
    
    return changes