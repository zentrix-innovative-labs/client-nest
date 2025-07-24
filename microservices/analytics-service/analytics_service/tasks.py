from celery import shared_task
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Generate synthetic time-series data (replace with real data later)
dates = pd.date_range(datetime.now() - timedelta(days=30), periods=31, freq='D')
engagement = 50 + 10 * np.sin(np.linspace(0, 3 * np.pi, 31)) + np.random.normal(0, 3, 31)
data = pd.DataFrame({'date': dates, 'engagement': engagement})

@shared_task
def batch_aggregate_engagement():
    """
    Example Celery task to batch process and aggregate engagement data.
    Replace synthetic data with real data when available.
    """
    # Aggregate by week
    data['week'] = data['date'].dt.isocalendar().week
    weekly_avg = data.groupby('week')['engagement'].mean()
    print("Weekly average engagement:")
    print(weekly_avg)
    # In production, store results in DB or send to another service
    return weekly_avg.to_dict() 