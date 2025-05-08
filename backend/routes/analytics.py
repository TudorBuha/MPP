from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, text
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models.database import get_db
from models.contact import ContactDB, TransactionDB

router = APIRouter()

@router.get("/statistics/transactions")
async def get_transaction_statistics(
    db: Session = Depends(get_db),
    period: str = Query("all", description="Time period: 'day', 'week', 'month', 'year', or 'all'")
):
    """
    Get statistics about transactions.
    This endpoint performs a complex statistical analysis on transaction data.
    """
    # Define time filters based on period
    now = datetime.now()
    time_filter = None
    
    if period == "day":
        time_filter = and_(TransactionDB.date >= now - timedelta(days=1))
    elif period == "week":
        time_filter = and_(TransactionDB.date >= now - timedelta(weeks=1))
    elif period == "month":
        time_filter = and_(TransactionDB.date >= now - timedelta(days=30))
    elif period == "year":
        time_filter = and_(TransactionDB.date >= now - timedelta(days=365))
    
    # Base query
    query = db.query(
        func.count(TransactionDB.id).label("total_count"),
        func.sum(TransactionDB.amount).label("total_amount"),
        func.avg(TransactionDB.amount).label("average_amount"),
        func.min(TransactionDB.amount).label("min_amount"),
        func.max(TransactionDB.amount).label("max_amount")
    )
    
    # Apply time filter if specified
    if time_filter:
        query = query.filter(time_filter)
    
    # Execute the query
    stats = query.one()
    
    # Get additional statistics with separate optimized queries
    
    # Top 10 contacts by transaction volume
    top_contacts_by_volume = db.query(
        ContactDB.id,
        ContactDB.name,
        func.count(TransactionDB.id).label("transaction_count")
    ).join(
        TransactionDB, ContactDB.id == TransactionDB.contact_id
    ).group_by(
        ContactDB.id
    ).order_by(
        desc("transaction_count")
    ).limit(10).all()
    
    # Top 10 contacts by transaction amount
    top_contacts_by_amount = db.query(
        ContactDB.id,
        ContactDB.name,
        func.sum(TransactionDB.amount).label("total_amount")
    ).join(
        TransactionDB, ContactDB.id == TransactionDB.contact_id
    ).group_by(
        ContactDB.id
    ).order_by(
        desc("total_amount")
    ).limit(10).all()
    
    # Distribution of transaction amounts by range
    ranges = {
        "negative_large": "amount < -500",
        "negative_medium": "amount BETWEEN -500 AND -100",
        "negative_small": "amount BETWEEN -100 AND 0",
        "positive_small": "amount BETWEEN 0 AND 100",
        "positive_medium": "amount BETWEEN 100 AND 500",
        "positive_large": "amount > 500"
    }
    
    amount_distribution = {}
    for name, condition in ranges.items():
        sql = f"SELECT COUNT(*) FROM transactions WHERE {condition}"
        if time_filter:
            # Add date condition if needed
            date_condition = ""
            if period == "day":
                date_condition = f" AND date >= datetime('now', '-1 day')"
            elif period == "week":
                date_condition = f" AND date >= datetime('now', '-7 day')"
            elif period == "month":
                date_condition = f" AND date >= datetime('now', '-30 day')"
            elif period == "year":
                date_condition = f" AND date >= datetime('now', '-365 day')"
            
            sql += date_condition
            
        result = db.execute(text(sql)).scalar()
        amount_distribution[name] = result
    
    # Return combined statistics
    return {
        "total_count": stats.total_count,
        "total_amount": float(stats.total_amount) if stats.total_amount else 0,
        "average_amount": float(stats.average_amount) if stats.average_amount else 0,
        "min_amount": float(stats.min_amount) if stats.min_amount else 0,
        "max_amount": float(stats.max_amount) if stats.max_amount else 0,
        "top_contacts_by_volume": [
            {"id": c.id, "name": c.name, "transaction_count": c.transaction_count}
            for c in top_contacts_by_volume
        ],
        "top_contacts_by_amount": [
            {"id": c.id, "name": c.name, "total_amount": float(c.total_amount)}
            for c in top_contacts_by_amount
        ],
        "amount_distribution": amount_distribution,
        "period": period
    }

@router.get("/statistics/transactions/monthly")
async def get_monthly_transaction_trends(
    db: Session = Depends(get_db),
    months: int = Query(12, description="Number of months to analyze", ge=1, le=60)
):
    """
    Get monthly trends for transactions.
    This endpoint analyzes transaction patterns over months.
    """
    # Generate a series of months
    now = datetime.now()
    month_data = []
    
    for i in range(months):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = month_start.month + 1 if month_start.month < 12 else 1
        next_year = month_start.year + 1 if month_start.month == 12 else month_start.year
        month_end = datetime(next_year, next_month, 1) - timedelta(microseconds=1)
        
        # For the current month, use current datetime as end
        if i == 0:
            month_end = now
            
        # Get transaction statistics for the month
        stats = db.query(
            func.count(TransactionDB.id).label("count"),
            func.sum(TransactionDB.amount).label("sum"),
            func.avg(TransactionDB.amount).label("avg")
        ).filter(
            TransactionDB.date >= month_start,
            TransactionDB.date <= month_end
        ).one()
        
        # Get positive and negative transaction counts
        positive_count = db.query(
            func.count(TransactionDB.id)
        ).filter(
            TransactionDB.date >= month_start,
            TransactionDB.date <= month_end,
            TransactionDB.amount > 0
        ).scalar()
        
        negative_count = db.query(
            func.count(TransactionDB.id)
        ).filter(
            TransactionDB.date >= month_start,
            TransactionDB.date <= month_end,
            TransactionDB.amount < 0
        ).scalar()
        
        # Format month name
        month_name = month_start.strftime("%B %Y")
        
        month_data.append({
            "month": month_name,
            "transaction_count": stats.count,
            "total_amount": float(stats.sum) if stats.sum else 0,
            "average_amount": float(stats.avg) if stats.avg else 0,
            "positive_count": positive_count,
            "negative_count": negative_count
        })
    
    # Return the reversed list so most recent month is first
    return {
        "monthly_trends": list(reversed(month_data)),
        "total_months": months
    }

@router.get("/statistics/contacts/tags")
async def get_tag_statistics(
    db: Session = Depends(get_db)
):
    """
    Get statistics about contact tags.
    This endpoint analyzes the distribution and performance of different tags.
    """
    # Count contacts by tag (take top 20)
    tag_counts = db.query(
        ContactDB.tag,
        func.count(ContactDB.id).label("contact_count")
    ).group_by(
        ContactDB.tag
    ).order_by(
        desc("contact_count")
    ).limit(20).all()
    
    # Get tags with highest average transaction amount
    tag_avg_transactions = db.query(
        ContactDB.tag,
        func.avg(TransactionDB.amount).label("avg_amount"),
        func.count(TransactionDB.id).label("transaction_count")
    ).join(
        TransactionDB, ContactDB.id == TransactionDB.contact_id
    ).group_by(
        ContactDB.tag
    ).having(
        func.count(TransactionDB.id) > 10  # Only consider tags with sufficient transactions
    ).order_by(
        desc("avg_amount")
    ).limit(10).all()
    
    # Get tags with most transactions
    tag_transaction_counts = db.query(
        ContactDB.tag,
        func.count(TransactionDB.id).label("transaction_count")
    ).join(
        TransactionDB, ContactDB.id == TransactionDB.contact_id
    ).group_by(
        ContactDB.tag
    ).order_by(
        desc("transaction_count")
    ).limit(10).all()
    
    return {
        "tag_counts": [
            {"tag": t.tag, "contact_count": t.contact_count}
            for t in tag_counts if t.tag  # Filter out None tags
        ],
        "tag_avg_transactions": [
            {"tag": t.tag, "avg_amount": float(t.avg_amount), "transaction_count": t.transaction_count}
            for t in tag_avg_transactions if t.tag  # Filter out None tags
        ],
        "tag_transaction_counts": [
            {"tag": t.tag, "transaction_count": t.transaction_count}
            for t in tag_transaction_counts if t.tag  # Filter out None tags
        ]
    } 