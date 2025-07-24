import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Generate synthetic time-series data (replace with real data later)
dates = pd.date_range(datetime.now() - timedelta(days=30), periods=31, freq='D')
engagement = 50 + 10 * np.sin(np.linspace(0, 3 * np.pi, 31)) + np.random.normal(0, 3, 31)
data = pd.DataFrame({'date': dates, 'engagement': engagement})

def generate_insights(metrics=None):
    """
    Analyze engagement time-series and return actionable insights.
    Args:
        metrics: Optional, not used in provisional version.
    Returns:
        list of str: Insights.
    """
    # Find the day of week with highest average engagement
    data['weekday'] = data['date'].dt.day_name()
    weekday_means = data.groupby('weekday')['engagement'].mean()
    best_day = weekday_means.idxmax()
    best_value = weekday_means.max()

    # Simple trend: is engagement increasing or decreasing?
    trend = np.polyfit(range(len(data)), data['engagement'], 1)[0]
    if trend > 0.2:
        trend_msg = "Engagement is trending upward."
    elif trend < -0.2:
        trend_msg = "Engagement is trending downward."
    else:
        trend_msg = "Engagement is stable."

    return [
        f"Your posts perform best on {best_day}s (avg. engagement: {best_value:.1f}).",
        trend_msg
    ] 