# ClientNest Data Science & Analytics Architecture

## Data Science Overview

ClientNest's data science architecture enables intelligent insights, predictive analytics, and data-driven decision making across social media management. The system processes user behavior, content performance, engagement patterns, and AI usage to provide actionable insights.

## Data Science Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DATA SCIENCE & ANALYTICS ARCHITECTURE                   │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA SOURCES                                      │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│  User Activity  │  Content Data   │  Social Media   │    AI Usage Data        │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Login Events  │ • Posts Created │ • Platform APIs │ • AI Requests           │
│ • Feature Usage │ • Engagement    │ • Comments      │ • Token Usage           │
│ • Session Data  │ • Scheduling    │ • Likes/Shares  │ • Cost Tracking         │
│ • Click Streams │ • Performance   │ • Followers     │ • Response Quality      │
│ • Error Events  │ • A/B Tests     │ • Reach Metrics │ • Processing Times      │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DATA INGESTION LAYER                                 │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│  Real-time      │  Batch ETL      │  API Collectors │    Event Streaming      │
│  Streaming      │  Pipelines      │                 │                         │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Kafka Streams │ • Airflow DAGs  │ • Social APIs   │ • User Events           │
│ • Event Bus     │ • Data Validation│ • Analytics APIs│ • System Events         │
│ • CDC Streams   │ • Transformation│ • Third-party   │ • Error Events          │
│ • Log Streams   │ • Data Quality  │   Integrations  │ • Performance Events    │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DATA STORAGE LAYER                                  │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Data Lake     │  Data Warehouse │   Time Series   │    Feature Store        │
│   (S3)          │  (Redshift)     │  (TimescaleDB)  │                         │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Raw Data      │ • Cleaned Data  │ • Metrics       │ • ML Features           │
│ • Logs          │ • Aggregations  │ • Time-based    │ • Feature Versions      │
│ • Backups       │ • Dimensions    │   Analytics     │ • Feature Lineage       │
│ • Archives      │ • Facts         │ • Real-time     │ • Feature Monitoring    │
│ • Unstructured  │ • Star Schema   │   Dashboards    │ • A/B Test Features     │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          ANALYTICS & ML LAYER                                  │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│  Descriptive    │  Predictive     │  Prescriptive   │    Real-time ML         │
│  Analytics      │  Analytics      │  Analytics      │                         │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • KPI Reports   │ • Engagement    │ • Content       │ • Anomaly Detection     │
│ • Dashboards    │   Prediction    │   Optimization  │ • Real-time Scoring     │
│ • Cohort        │ • Churn Models  │ • Posting Time  │ • Dynamic Pricing       │
│   Analysis      │ • Growth Models │   Optimization  │ • Fraud Detection       │
│ • Funnel        │ • Content       │ • Budget        │ • Content Filtering     │
│   Analysis      │   Performance   │   Allocation    │ • Personalization      │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INSIGHTS & DELIVERY                                  │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Dashboards    │   API Endpoints │   Alerts &      │    Recommendations      │
│   & Reports     │                 │   Notifications │                         │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ • Executive     │ • Analytics API │ • Threshold     │ • Content Suggestions   │
│   Dashboard     │ • ML Model API  │   Alerts        │ • Posting Time          │
│ • User          │ • Insights API  │ • Anomaly       │ • Hashtag Suggestions   │
│   Analytics     │ • Reporting API │   Detection     │ • Audience Insights     │
│ • Performance   │ • Export API    │ • Performance   │ • Growth Strategies     │
│   Reports       │ • Webhook API   │   Warnings      │ • Content Optimization  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## Data Pipeline Architecture

### ETL Pipeline Implementation

```python
# backend/analytics/etl/data_pipeline.py
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
import logging
import boto3
from sqlalchemy import create_engine
import redis

logger = logging.getLogger('analytics.etl')

class DataPipeline:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.redshift_engine = create_engine(settings.REDSHIFT_URL)
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.timescale_engine = create_engine(settings.TIMESCALE_URL)
    
    async def run_daily_etl(self):
        """Run daily ETL pipeline"""
        
        logger.info('Starting daily ETL pipeline')
        
        try:
            # Extract data from various sources
            user_data = await self.extract_user_activity_data()
            content_data = await self.extract_content_performance_data()
            social_data = await self.extract_social_media_data()
            ai_data = await self.extract_ai_usage_data()
            
            # Transform data
            transformed_data = await self.transform_data({
                'users': user_data,
                'content': content_data,
                'social': social_data,
                'ai': ai_data
            })
            
            # Load to data warehouse
            await self.load_to_warehouse(transformed_data)
            
            # Update feature store
            await self.update_feature_store(transformed_data)
            
            # Generate daily insights
            await self.generate_daily_insights()
            
            logger.info('Daily ETL pipeline completed successfully')
            
        except Exception as e:
            logger.error(f'Daily ETL pipeline failed: {str(e)}')
            raise
    
    async def extract_user_activity_data(self) -> pd.DataFrame:
        """Extract user activity data from PostgreSQL"""
        
        query = """
        SELECT 
            u.id as user_id,
            u.subscription_tier,
            u.date_joined,
            u.last_login,
            COUNT(DISTINCT s.id) as sessions_count,
            COUNT(DISTINCT p.id) as posts_created,
            COUNT(DISTINCT sm.id) as social_accounts,
            AVG(s.duration) as avg_session_duration,
            COUNT(DISTINCT DATE(s.created_at)) as active_days
        FROM auth_user u
        LEFT JOIN user_sessions s ON u.id = s.user_id 
            AND s.created_at >= CURRENT_DATE - INTERVAL '1 day'
        LEFT JOIN social_posts p ON u.id = p.user_id 
            AND p.created_at >= CURRENT_DATE - INTERVAL '1 day'
        LEFT JOIN social_media_accounts sm ON u.id = sm.user_id
        WHERE u.is_active = true
        GROUP BY u.id, u.subscription_tier, u.date_joined, u.last_login
        """
        
        return pd.read_sql(query, self.redshift_engine)
    
    async def extract_content_performance_data(self) -> pd.DataFrame:
        """Extract content performance data"""
        
        query = """
        SELECT 
            p.id as post_id,
            p.user_id,
            p.platform,
            p.content,
            p.scheduled_time,
            p.published_time,
            p.status,
            pm.likes_count,
            pm.comments_count,
            pm.shares_count,
            pm.reach,
            pm.impressions,
            pm.engagement_rate,
            pm.click_through_rate,
            LENGTH(p.content) as content_length,
            ARRAY_LENGTH(p.hashtags, 1) as hashtag_count,
            CASE WHEN p.ai_generated = true THEN 1 ELSE 0 END as is_ai_generated
        FROM social_posts p
        LEFT JOIN post_metrics pm ON p.id = pm.post_id
        WHERE p.created_at >= CURRENT_DATE - INTERVAL '1 day'
        """
        
        return pd.read_sql(query, self.redshift_engine)
    
    async def extract_social_media_data(self) -> pd.DataFrame:
        """Extract social media platform data"""
        
        query = """
        SELECT 
            sma.id as account_id,
            sma.user_id,
            sma.platform,
            sma.followers_count,
            sma.following_count,
            sma.posts_count,
            sma.engagement_rate,
            sma.last_sync,
            COUNT(DISTINCT c.id) as comments_received,
            AVG(CASE WHEN sa.sentiment = 'positive' THEN 1 
                     WHEN sa.sentiment = 'negative' THEN -1 
                     ELSE 0 END) as avg_sentiment
        FROM social_media_accounts sma
        LEFT JOIN social_comments c ON sma.id = c.account_id 
            AND c.created_at >= CURRENT_DATE - INTERVAL '1 day'
        LEFT JOIN sentiment_analysis sa ON c.id = sa.comment_id
        GROUP BY sma.id, sma.user_id, sma.platform, sma.followers_count, 
                 sma.following_count, sma.posts_count, sma.engagement_rate, sma.last_sync
        """
        
        return pd.read_sql(query, self.redshift_engine)
    
    async def extract_ai_usage_data(self) -> pd.DataFrame:
        """Extract AI usage and performance data"""
        
        query = """
        SELECT 
            ar.id as request_id,
            ar.user_id,
            ar.request_type,
            ar.platform,
            ar.status,
            ar.created_at,
            ar.completed_at,
            EXTRACT(EPOCH FROM (ar.completed_at - ar.started_at)) as processing_time,
            aul.tokens_used,
            aul.cost,
            cg.quality_score,
            CASE WHEN ar.request_type = 'content_generation' THEN 1 ELSE 0 END as is_content_gen,
            CASE WHEN ar.request_type = 'sentiment_analysis' THEN 1 ELSE 0 END as is_sentiment,
            CASE WHEN ar.request_type = 'content_optimization' THEN 1 ELSE 0 END as is_optimization
        FROM ai_requests ar
        LEFT JOIN ai_usage_logs aul ON ar.id = aul.request_id
        LEFT JOIN content_generations cg ON ar.id = cg.ai_request_id
        WHERE ar.created_at >= CURRENT_DATE - INTERVAL '1 day'
        """
        
        return pd.read_sql(query, self.redshift_engine)
    
    async def transform_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform and clean extracted data"""
        
        transformed = {}
        
        # Transform user data
        users_df = raw_data['users'].copy()
        users_df['user_tenure_days'] = (datetime.now() - pd.to_datetime(users_df['date_joined'])).dt.days
        users_df['days_since_last_login'] = (datetime.now() - pd.to_datetime(users_df['last_login'])).dt.days
        users_df['is_active_user'] = users_df['days_since_last_login'] <= 7
        users_df['user_segment'] = users_df.apply(self._categorize_user, axis=1)
        transformed['users'] = users_df
        
        # Transform content data
        content_df = raw_data['content'].copy()
        content_df['engagement_score'] = (
            content_df['likes_count'] * 1 + 
            content_df['comments_count'] * 2 + 
            content_df['shares_count'] * 3
        ).fillna(0)
        content_df['content_category'] = content_df['content'].apply(self._categorize_content)
        content_df['posting_hour'] = pd.to_datetime(content_df['published_time']).dt.hour
        content_df['posting_day'] = pd.to_datetime(content_df['published_time']).dt.day_name()
        content_df['performance_tier'] = pd.qcut(content_df['engagement_score'], 
                                               q=4, labels=['Low', 'Medium', 'High', 'Viral'])
        transformed['content'] = content_df
        
        # Transform social media data
        social_df = raw_data['social'].copy()
        social_df['follower_growth_rate'] = social_df.groupby('user_id')['followers_count'].pct_change()
        social_df['engagement_category'] = pd.cut(social_df['engagement_rate'], 
                                                bins=[0, 0.01, 0.03, 0.06, 1], 
                                                labels=['Low', 'Medium', 'High', 'Excellent'])
        transformed['social'] = social_df
        
        # Transform AI data
        ai_df = raw_data['ai'].copy()
        ai_df['cost_per_token'] = ai_df['cost'] / ai_df['tokens_used'].replace(0, 1)
        ai_df['processing_speed'] = ai_df['tokens_used'] / ai_df['processing_time'].replace(0, 1)
        ai_df['efficiency_score'] = ai_df['quality_score'] / ai_df['cost'].replace(0, 1)
        transformed['ai'] = ai_df
        
        return transformed
    
    def _categorize_user(self, row) -> str:
        """Categorize users based on activity and tenure"""
        if row['user_tenure_days'] < 7:
            return 'New'
        elif row['is_active_user'] and row['sessions_count'] > 10:
            return 'Power User'
        elif row['is_active_user']:
            return 'Active'
        elif row['days_since_last_login'] <= 30:
            return 'Inactive'
        else:
            return 'Churned'
    
    def _categorize_content(self, content: str) -> str:
        """Categorize content based on keywords and patterns"""
        if not content:
            return 'Unknown'
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['sale', 'discount', 'offer', 'buy']):
            return 'Promotional'
        elif any(word in content_lower for word in ['tip', 'how to', 'guide', 'tutorial']):
            return 'Educational'
        elif any(word in content_lower for word in ['behind', 'team', 'story', 'journey']):
            return 'Behind the Scenes'
        elif any(word in content_lower for word in ['question', '?', 'poll', 'vote']):
            return 'Interactive'
        else:
            return 'General'
    
    async def load_to_warehouse(self, transformed_data: Dict[str, pd.DataFrame]):
        """Load transformed data to data warehouse"""
        
        for table_name, df in transformed_data.items():
            try:
                # Add ETL metadata
                df['etl_date'] = datetime.now().date()
                df['etl_timestamp'] = datetime.now()
                
                # Load to Redshift
                df.to_sql(
                    f'fact_{table_name}_daily',
                    self.redshift_engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                
                logger.info(f'Loaded {len(df)} records to fact_{table_name}_daily')
                
            except Exception as e:
                logger.error(f'Failed to load {table_name} data: {str(e)}')
                raise
    
    async def update_feature_store(self, transformed_data: Dict[str, pd.DataFrame]):
        """Update ML feature store with latest features"""
        
        # Generate user features
        user_features = await self._generate_user_features(transformed_data['users'])
        
        # Generate content features
        content_features = await self._generate_content_features(transformed_data['content'])
        
        # Store features in Redis for real-time ML
        for user_id, features in user_features.items():
            self.redis_client.hset(
                f'user_features:{user_id}',
                mapping=features
            )
            self.redis_client.expire(f'user_features:{user_id}', 86400)  # 24 hours
        
        logger.info(f'Updated features for {len(user_features)} users')
    
    async def _generate_user_features(self, users_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Generate ML features for users"""
        
        features = {}
        
        for _, user in users_df.iterrows():
            user_id = str(user['user_id'])
            
            features[user_id] = {
                'tenure_days': float(user['user_tenure_days']),
                'avg_session_duration': float(user['avg_session_duration'] or 0),
                'posts_per_day': float(user['posts_created']),
                'social_accounts_count': float(user['social_accounts']),
                'activity_score': float(user['sessions_count'] * user['active_days']),
                'subscription_tier_encoded': self._encode_subscription_tier(user['subscription_tier']),
                'is_power_user': 1.0 if user['user_segment'] == 'Power User' else 0.0,
                'churn_risk': self._calculate_churn_risk(user)
            }
        
        return features
    
    def _encode_subscription_tier(self, tier: str) -> float:
        """Encode subscription tier as numeric value"""
        tier_mapping = {
            'free': 0.0,
            'starter': 1.0,
            'professional': 2.0,
            'business': 3.0,
            'enterprise': 4.0
        }
        return tier_mapping.get(tier, 0.0)
    
    def _calculate_churn_risk(self, user: pd.Series) -> float:
        """Calculate churn risk score for user"""
        risk_score = 0.0
        
        # Days since last login
        if user['days_since_last_login'] > 14:
            risk_score += 0.3
        elif user['days_since_last_login'] > 7:
            risk_score += 0.1
        
        # Session activity
        if user['sessions_count'] < 2:
            risk_score += 0.2
        
        # Content creation
        if user['posts_created'] == 0:
            risk_score += 0.2
        
        # Account setup
        if user['social_accounts'] == 0:
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    async def _generate_content_features(self, content_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Generate ML features for content"""
        
        features = {}
        
        for _, content in content_df.iterrows():
            post_id = str(content['post_id'])
            
            features[post_id] = {
                'content_length': float(content['content_length']),
                'hashtag_count': float(content['hashtag_count'] or 0),
                'posting_hour': float(content['posting_hour']),
                'is_ai_generated': float(content['is_ai_generated']),
                'engagement_score': float(content['engagement_score']),
                'platform_encoded': self._encode_platform(content['platform']),
                'content_category_encoded': self._encode_content_category(content['content_category'])
            }
        
        return features
    
    def _encode_platform(self, platform: str) -> float:
        """Encode platform as numeric value"""
        platform_mapping = {
            'twitter': 1.0,
            'facebook': 2.0,
            'instagram': 3.0,
            'linkedin': 4.0,
            'tiktok': 5.0
        }
        return platform_mapping.get(platform, 0.0)
    
    def _encode_content_category(self, category: str) -> float:
        """Encode content category as numeric value"""
        category_mapping = {
            'Promotional': 1.0,
            'Educational': 2.0,
            'Behind the Scenes': 3.0,
            'Interactive': 4.0,
            'General': 5.0
        }
        return category_mapping.get(category, 0.0)
    
    async def generate_daily_insights(self):
        """Generate daily insights and alerts"""
        
        # Calculate key metrics
        metrics = await self._calculate_daily_metrics()
        
        # Detect anomalies
        anomalies = await self._detect_anomalies(metrics)
        
        # Generate alerts
        if anomalies:
            await self._send_alerts(anomalies)
        
        # Update dashboard cache
        await self._update_dashboard_cache(metrics)
        
        logger.info('Daily insights generated successfully')
    
    async def _calculate_daily_metrics(self) -> Dict[str, float]:
        """Calculate key daily metrics"""
        
        query = """
        SELECT 
            COUNT(DISTINCT user_id) as active_users,
            COUNT(DISTINCT CASE WHEN subscription_tier != 'free' THEN user_id END) as paying_users,
            COUNT(*) as total_posts,
            AVG(engagement_score) as avg_engagement,
            SUM(CASE WHEN is_ai_generated = 1 THEN 1 ELSE 0 END) as ai_generated_posts,
            AVG(processing_time) as avg_ai_processing_time,
            SUM(cost) as total_ai_cost
        FROM fact_users_daily u
        JOIN fact_content_daily c ON u.user_id = c.user_id
        JOIN fact_ai_daily a ON u.user_id = a.user_id
        WHERE etl_date = CURRENT_DATE
        """
        
        result = pd.read_sql(query, self.redshift_engine)
        return result.iloc[0].to_dict()
    
    async def _detect_anomalies(self, current_metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect anomalies in daily metrics"""
        
        anomalies = []
        
        # Get historical averages (last 30 days)
        historical_query = """
        SELECT 
            AVG(active_users) as avg_active_users,
            STDDEV(active_users) as std_active_users,
            AVG(avg_engagement) as avg_engagement_score,
            STDDEV(avg_engagement) as std_engagement_score,
            AVG(total_ai_cost) as avg_ai_cost,
            STDDEV(total_ai_cost) as std_ai_cost
        FROM (
            SELECT 
                etl_date,
                COUNT(DISTINCT user_id) as active_users,
                AVG(engagement_score) as avg_engagement,
                SUM(cost) as total_ai_cost
            FROM fact_users_daily u
            JOIN fact_content_daily c ON u.user_id = c.user_id
            JOIN fact_ai_daily a ON u.user_id = a.user_id
            WHERE etl_date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY etl_date
        ) daily_metrics
        """
        
        historical = pd.read_sql(historical_query, self.redshift_engine).iloc[0]
        
        # Check for anomalies (2 standard deviations)
        for metric in ['active_users', 'avg_engagement', 'total_ai_cost']:
            current_value = current_metrics.get(metric, 0)
            avg_value = historical.get(f'avg_{metric}', 0)
            std_value = historical.get(f'std_{metric}', 0)
            
            if std_value > 0:
                z_score = abs(current_value - avg_value) / std_value
                
                if z_score > 2:  # Anomaly detected
                    anomalies.append({
                        'metric': metric,
                        'current_value': current_value,
                        'expected_value': avg_value,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium'
                    })
        
        return anomalies
    
    async def _send_alerts(self, anomalies: List[Dict[str, Any]]):
        """Send alerts for detected anomalies"""
        
        for anomaly in anomalies:
            logger.warning(f"Anomaly detected: {anomaly}")
            
            # Send to monitoring system
            # Implementation depends on monitoring setup (e.g., Slack, email, PagerDuty)
    
    async def _update_dashboard_cache(self, metrics: Dict[str, float]):
        """Update dashboard cache with latest metrics"""
        
        # Cache metrics for dashboard
        self.redis_client.hset(
            'dashboard:daily_metrics',
            mapping={k: str(v) for k, v in metrics.items()}
        )
        self.redis_client.expire('dashboard:daily_metrics', 86400)
        
        # Update time series data
        timestamp = int(datetime.now().timestamp())
        for metric, value in metrics.items():
            self.redis_client.zadd(
                f'timeseries:{metric}',
                {timestamp: value}
            )
            # Keep only last 30 days
            cutoff = timestamp - (30 * 24 * 3600)
            self.redis_client.zremrangebyscore(f'timeseries:{metric}', 0, cutoff)
```

### Machine Learning Models

```python
# backend/analytics/ml/models.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger('analytics.ml')

class EngagementPredictionModel:
    """Predict content engagement based on features"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'content_length', 'hashtag_count', 'posting_hour',
            'is_ai_generated', 'platform_encoded', 'content_category_encoded',
            'user_followers', 'user_engagement_history', 'day_of_week'
        ]
        self.is_trained = False
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for training or prediction"""
        
        features = data.copy()
        
        # Add derived features
        features['day_of_week'] = pd.to_datetime(features['published_time']).dt.dayofweek
        features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        features['content_length_log'] = np.log1p(features['content_length'])
        
        # Handle missing values
        features = features.fillna(0)
        
        return features[self.feature_columns]
    
    def train(self, training_data: pd.DataFrame, target_column: str = 'engagement_score'):
        """Train the engagement prediction model"""
        
        logger.info('Training engagement prediction model')
        
        # Prepare features and target
        X = self.prepare_features(training_data)
        y = training_data[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        logger.info(f'Model trained - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}')
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f'Top features: {importance.head().to_dict("records")}')
        
        self.is_trained = True
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'feature_importance': importance.to_dict('records')
        }
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict engagement for new content"""
        
        if not self.is_trained:
            raise ValueError('Model must be trained before prediction')
        
        X = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        return np.maximum(predictions, 0)  # Ensure non-negative predictions
    
    def save_model(self, filepath: str):
        """Save trained model to file"""
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f'Model saved to {filepath}')
    
    def load_model(self, filepath: str):
        """Load trained model from file"""
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
        
        logger.info(f'Model loaded from {filepath}')

class ChurnPredictionModel:
    """Predict user churn probability"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'tenure_days', 'days_since_last_login', 'avg_session_duration',
            'posts_per_week', 'social_accounts_count', 'subscription_tier_encoded',
            'ai_usage_frequency', 'engagement_trend', 'support_tickets'
        ]
        self.is_trained = False
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for churn prediction"""
        
        features = data.copy()
        
        # Calculate derived features
        features['posts_per_week'] = features['posts_created'] / (features['tenure_days'] / 7 + 1)
        features['ai_usage_frequency'] = features['ai_requests_count'] / (features['tenure_days'] + 1)
        features['engagement_trend'] = features['recent_engagement'] - features['historical_engagement']
        
        # Handle missing values
        features = features.fillna(0)
        
        return features[self.feature_columns]
    
    def train(self, training_data: pd.DataFrame, target_column: str = 'churned'):
        """Train the churn prediction model"""
        
        logger.info('Training churn prediction model')
        
        # Prepare features and target
        X = self.prepare_features(training_data)
        y = training_data[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        logger.info(f'Churn model - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, '
                   f'Recall: {recall:.3f}, F1: {f1:.3f}')
        
        self.is_trained = True
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def predict_proba(self, data: pd.DataFrame) -> np.ndarray:
        """Predict churn probability"""
        
        if not self.is_trained:
            raise ValueError('Model must be trained before prediction')
        
        X = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        # Return probability of churn (class 1)
        return self.model.predict_proba(X_scaled)[:, 1]
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance for interpretability"""
        
        if not self.is_trained:
            raise ValueError('Model must be trained first')
        
        importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance

class OptimalPostingTimeModel:
    """Predict optimal posting times for maximum engagement"""
    
    def __init__(self):
        self.platform_models = {}
        self.is_trained = False
    
    def train(self, training_data: pd.DataFrame):
        """Train optimal posting time models for each platform"""
        
        logger.info('Training optimal posting time models')
        
        for platform in training_data['platform'].unique():
            platform_data = training_data[training_data['platform'] == platform]
            
            if len(platform_data) < 100:  # Skip if insufficient data
                continue
            
            # Create time-based features
            platform_data['hour'] = pd.to_datetime(platform_data['published_time']).dt.hour
            platform_data['day_of_week'] = pd.to_datetime(platform_data['published_time']).dt.dayofweek
            
            # Calculate average engagement by time slots
            engagement_by_time = platform_data.groupby(['hour', 'day_of_week'])['engagement_score'].agg([
                'mean', 'count', 'std'
            ]).reset_index()
            
            # Filter out time slots with insufficient data
            engagement_by_time = engagement_by_time[engagement_by_time['count'] >= 5]
            
            self.platform_models[platform] = engagement_by_time
        
        self.is_trained = True
        logger.info(f'Trained models for {len(self.platform_models)} platforms')
    
    def get_optimal_times(self, platform: str, user_timezone: str = 'UTC') -> List[Dict[str, Any]]:
        """Get optimal posting times for a platform"""
        
        if not self.is_trained or platform not in self.platform_models:
            return []
        
        model_data = self.platform_models[platform]
        
        # Get top 5 time slots
        top_times = model_data.nlargest(5, 'mean')[['hour', 'day_of_week', 'mean']]
        
        optimal_times = []
        for _, row in top_times.iterrows():
            optimal_times.append({
                'hour': int(row['hour']),
                'day_of_week': int(row['day_of_week']),
                'day_name': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                           'Friday', 'Saturday', 'Sunday'][int(row['day_of_week'])],
                'expected_engagement': float(row['mean']),
                'confidence': 'high' if row['mean'] > model_data['mean'].quantile(0.8) else 'medium'
            })
        
        return optimal_times

class ContentRecommendationModel:
    """Recommend content topics and strategies"""
    
    def __init__(self):
        self.topic_performance = {}
        self.user_preferences = {}
        self.is_trained = False
    
    def train(self, content_data: pd.DataFrame, user_data: pd.DataFrame):
        """Train content recommendation model"""
        
        logger.info('Training content recommendation model')
        
        # Analyze topic performance
        self.topic_performance = content_data.groupby('content_category').agg({
            'engagement_score': ['mean', 'std', 'count'],
            'reach': 'mean',
            'click_through_rate': 'mean'
        }).round(3)
        
        # Analyze user preferences
        user_content = content_data.merge(user_data, on='user_id')
        
        self.user_preferences = user_content.groupby(['subscription_tier', 'content_category']).agg({
            'engagement_score': 'mean',
            'user_id': 'count'
        }).rename(columns={'user_id': 'post_count'})
        
        self.is_trained = True
        logger.info('Content recommendation model trained')
    
    def get_recommendations(self, user_tier: str, platform: str, 
                          recent_performance: Dict[str, float]) -> List[Dict[str, Any]]:
        """Get content recommendations for user"""
        
        if not self.is_trained:
            return []
        
        recommendations = []
        
        # Get top performing content categories
        for category in self.topic_performance.index:
            avg_engagement = self.topic_performance.loc[category, ('engagement_score', 'mean')]
            category_count = self.topic_performance.loc[category, ('engagement_score', 'count')]
            
            if category_count < 10:  # Skip categories with insufficient data
                continue
            
            # Calculate recommendation score
            base_score = avg_engagement
            
            # Boost score for user's tier preferences
            if (user_tier, category) in self.user_preferences.index:
                tier_performance = self.user_preferences.loc[(user_tier, category), 'engagement_score']
                base_score = (base_score + tier_performance) / 2
            
            # Adjust based on user's recent performance
            user_category_performance = recent_performance.get(category, 0)
            if user_category_performance > 0:
                base_score = (base_score + user_category_performance) / 2
            
            recommendations.append({
                'category': category,
                'expected_engagement': float(base_score),
                'confidence': 'high' if category_count > 50 else 'medium',
                'sample_count': int(category_count)
            })
        
        # Sort by expected engagement
        recommendations.sort(key=lambda x: x['expected_engagement'], reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
```

### Analytics API Endpoints

```python
# backend/analytics/api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from ..ml.models import EngagementPredictionModel, ChurnPredictionModel
from ..etl.data_pipeline import DataPipeline
import logging

logger = logging.getLogger('analytics.api')

class UserAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user analytics dashboard data"""
        
        user = request.user
        time_range = request.query_params.get('range', '30d')  # 7d, 30d, 90d
        
        try:
            # Calculate date range
            end_date = timezone.now().date()
            if time_range == '7d':
                start_date = end_date - timedelta(days=7)
            elif time_range == '90d':
                start_date = end_date - timedelta(days=90)
            else:  # 30d default
                start_date = end_date - timedelta(days=30)
            
            # Get user metrics
            metrics = self._get_user_metrics(user, start_date, end_date)
            
            # Get content performance
            content_performance = self._get_content_performance(user, start_date, end_date)
            
            # Get AI usage stats
            ai_usage = self._get_ai_usage_stats(user, start_date, end_date)
            
            # Get growth trends
            growth_trends = self._get_growth_trends(user, start_date, end_date)
            
            return Response({
                'user_id': user.id,
                'time_range': time_range,
                'metrics': metrics,
                'content_performance': content_performance,
                'ai_usage': ai_usage,
                'growth_trends': growth_trends
            })
            
        except Exception as e:
            logger.error(f'Error getting user analytics: {str(e)}')
            return Response(
                {'error': 'Failed to retrieve analytics data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_user_metrics(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get basic user metrics"""
        
        from social.models import Post, SocialMediaAccount
        from ai.models import AIRequest
        
        # Posts metrics
        posts = Post.objects.filter(
            user=user,
            created_at__date__range=[start_date, end_date]
        )
        
        total_posts = posts.count()
        published_posts = posts.filter(status='published').count()
        scheduled_posts = posts.filter(status='scheduled').count()
        
        # Engagement metrics
        total_likes = sum(post.metrics.likes_count or 0 for post in posts if hasattr(post, 'metrics'))
        total_comments = sum(post.metrics.comments_count or 0 for post in posts if hasattr(post, 'metrics'))
        total_shares = sum(post.metrics.shares_count or 0 for post in posts if hasattr(post, 'metrics'))
        
        # AI usage
        ai_requests = AIRequest.objects.filter(
            user=user,
            created_at__date__range=[start_date, end_date]
        ).count()
        
        # Social accounts
        social_accounts = SocialMediaAccount.objects.filter(user=user).count()
        
        return {
            'total_posts': total_posts,
            'published_posts': published_posts,
            'scheduled_posts': scheduled_posts,
            'total_engagement': total_likes + total_comments + total_shares,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'ai_requests': ai_requests,
            'social_accounts': social_accounts,
            'avg_posts_per_day': total_posts / ((end_date - start_date).days + 1)
        }
    
    def _get_content_performance(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get content performance breakdown"""
        
        from social.models import Post
        
        posts = Post.objects.filter(
            user=user,
            created_at__date__range=[start_date, end_date],
            status='published'
        ).select_related('metrics')
        
        # Performance by platform
        platform_performance = {}
        for post in posts:
            platform = post.platform
            if platform not in platform_performance:
                platform_performance[platform] = {
                    'posts': 0,
                    'total_engagement': 0,
                    'avg_engagement': 0
                }
            
            engagement = 0
            if hasattr(post, 'metrics') and post.metrics:
                engagement = (post.metrics.likes_count or 0) + \
                           (post.metrics.comments_count or 0) + \
                           (post.metrics.shares_count or 0)
            
            platform_performance[platform]['posts'] += 1
            platform_performance[platform]['total_engagement'] += engagement
        
        # Calculate averages
        for platform in platform_performance:
            posts_count = platform_performance[platform]['posts']
            if posts_count > 0:
                platform_performance[platform]['avg_engagement'] = \
                    platform_performance[platform]['total_engagement'] / posts_count
        
        # Top performing posts
        top_posts = []
        for post in posts:
            engagement = 0
            if hasattr(post, 'metrics') and post.metrics:
                engagement = (post.metrics.likes_count or 0) + \
                           (post.metrics.comments_count or 0) + \
                           (post.metrics.shares_count or 0)
            
            top_posts.append({
                'id': post.id,
                'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'platform': post.platform,
                'engagement': engagement,
                'published_time': post.published_time
            })
        
        # Sort by engagement and take top 5
        top_posts.sort(key=lambda x: x['engagement'], reverse=True)
        top_posts = top_posts[:5]
        
        return {
            'platform_performance': platform_performance,
            'top_posts': top_posts
        }
    
    def _get_ai_usage_stats(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get AI usage statistics"""
        
        from ai.models import AIRequest, AIUsageLog
        
        # AI requests by type
        ai_requests = AIRequest.objects.filter(
            user=user,
            created_at__date__range=[start_date, end_date]
        )
        
        request_types = {}
        for request in ai_requests:
            req_type = request.request_type
            if req_type not in request_types:
                request_types[req_type] = 0
            request_types[req_type] += 1
        
        # Usage costs
        usage_logs = AIUsageLog.objects.filter(
            user=user,
            timestamp__date__range=[start_date, end_date]
        )
        
        total_cost = sum(log.cost for log in usage_logs)
        total_tokens = sum(log.tokens_used for log in usage_logs)
        
        return {
            'total_requests': ai_requests.count(),
            'request_types': request_types,
            'total_cost': float(total_cost),
            'total_tokens': total_tokens,
            'avg_cost_per_request': float(total_cost / ai_requests.count()) if ai_requests.count() > 0 else 0
        }
    
    def _get_growth_trends(self, user, start_date, end_date) -> Dict[str, Any]:
        """Get growth trends over time"""
        
        from social.models import Post, SocialMediaAccount
        
        # Daily post counts
        daily_posts = {}
        current_date = start_date
        while current_date <= end_date:
            posts_count = Post.objects.filter(
                user=user,
                created_at__date=current_date
            ).count()
            daily_posts[current_date.isoformat()] = posts_count
            current_date += timedelta(days=1)
        
        # Follower growth (if available)
        follower_growth = {}
        for account in SocialMediaAccount.objects.filter(user=user):
            # This would require historical follower data
            # For now, return current count
            follower_growth[account.platform] = account.followers_count or 0
        
        return {
            'daily_posts': daily_posts,
            'follower_growth': follower_growth
        }

class ContentPredictionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Predict content engagement"""
        
        try:
            # Get content data from request
            content_data = request.data
            
            # Validate required fields
            required_fields = ['content', 'platform', 'posting_time']
            for field in required_fields:
                if field not in content_data:
                    return Response(
                        {'error': f'Missing required field: {field}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Load trained model
            model = EngagementPredictionModel()
            model.load_model('/path/to/engagement_model.joblib')
            
            # Prepare data for prediction
            df = pd.DataFrame([{
                'content_length': len(content_data['content']),
                'hashtag_count': len(content_data.get('hashtags', [])),
                'posting_hour': pd.to_datetime(content_data['posting_time']).hour,
                'is_ai_generated': 1 if content_data.get('ai_generated', False) else 0,
                'platform_encoded': self._encode_platform(content_data['platform']),
                'content_category_encoded': self._encode_content_category(
                    content_data.get('category', 'General')
                ),
                'user_followers': self._get_user_followers(request.user),
                'user_engagement_history': self._get_user_avg_engagement(request.user),
                'day_of_week': pd.to_datetime(content_data['posting_time']).dayofweek,
                'published_time': content_data['posting_time']
            }])
            
            # Make prediction
            predicted_engagement = model.predict(df)[0]
            
            # Get confidence interval (simplified)
            confidence_low = max(0, predicted_engagement * 0.8)
            confidence_high = predicted_engagement * 1.2
            
            return Response({
                'predicted_engagement': float(predicted_engagement),
                'confidence_interval': {
                    'low': float(confidence_low),
                    'high': float(confidence_high)
                },
                'recommendation': self._get_engagement_recommendation(predicted_engagement)
            })
            
        except Exception as e:
            logger.error(f'Error predicting content engagement: {str(e)}')
            return Response(
                {'error': 'Failed to predict engagement'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _encode_platform(self, platform: str) -> float:
        """Encode platform as numeric value"""
        platform_mapping = {
            'twitter': 1.0, 'facebook': 2.0, 'instagram': 3.0,
            'linkedin': 4.0, 'tiktok': 5.0
        }
        return platform_mapping.get(platform.lower(), 0.0)
    
    def _encode_content_category(self, category: str) -> float:
        """Encode content category as numeric value"""
        category_mapping = {
            'promotional': 1.0, 'educational': 2.0, 'behind the scenes': 3.0,
            'interactive': 4.0, 'general': 5.0
        }
        return category_mapping.get(category.lower(), 5.0)
    
    def _get_user_followers(self, user) -> float:
        """Get user's total followers across platforms"""
        from social.models import SocialMediaAccount
        
        total_followers = SocialMediaAccount.objects.filter(user=user).aggregate(
            total=models.Sum('followers_count')
        )['total'] or 0
        
        return float(total_followers)
    
    def _get_user_avg_engagement(self, user) -> float:
        """Get user's average engagement rate"""
        from social.models import Post
        
        recent_posts = Post.objects.filter(
            user=user,
            status='published',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('metrics')
        
        if not recent_posts:
            return 0.0
        
        total_engagement = 0
        post_count = 0
        
        for post in recent_posts:
            if hasattr(post, 'metrics') and post.metrics:
                engagement = (post.metrics.likes_count or 0) + \
                           (post.metrics.comments_count or 0) + \
                           (post.metrics.shares_count or 0)
                total_engagement += engagement
                post_count += 1
        
        return float(total_engagement / post_count) if post_count > 0 else 0.0
    
    def _get_engagement_recommendation(self, predicted_engagement: float) -> str:
        """Get recommendation based on predicted engagement"""
        
        if predicted_engagement > 100:
            return "Excellent! This content is predicted to perform very well."
        elif predicted_engagement > 50:
            return "Good potential. Consider optimizing posting time for better reach."
        elif predicted_engagement > 20:
            return "Moderate performance expected. Try adding more engaging elements."
        else:
            return "Low engagement predicted. Consider revising content or trying a different approach."

class OptimalTimingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get optimal posting times for user's platforms"""
        
        try:
            platform = request.query_params.get('platform')
            user_timezone = request.query_params.get('timezone', 'UTC')
            
            # Load trained model
            model = OptimalPostingTimeModel()
            # In production, load from saved model file
            # model.load_model('/path/to/timing_model.joblib')
            
            if platform:
                # Get optimal times for specific platform
                optimal_times = model.get_optimal_times(platform, user_timezone)
                return Response({
                    'platform': platform,
                    'optimal_times': optimal_times
                })
            else:
                # Get optimal times for all user's platforms
                from social.models import SocialMediaAccount
                
                user_platforms = SocialMediaAccount.objects.filter(
                    user=request.user
                ).values_list('platform', flat=True).distinct()
                
                all_optimal_times = {}
                for platform in user_platforms:
                    all_optimal_times[platform] = model.get_optimal_times(platform, user_timezone)
                
                return Response({
                    'optimal_times_by_platform': all_optimal_times
                })
                
        except Exception as e:
            logger.error(f'Error getting optimal timing: {str(e)}')
            return Response(
                {'error': 'Failed to get optimal timing data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ContentRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get content recommendations for user"""
        
        try:
            platform = request.query_params.get('platform', 'all')
            
            # Get user's subscription tier
            user_tier = request.user.subscription_tier
            
            # Get user's recent performance by category
            recent_performance = self._get_recent_performance_by_category(request.user)
            
            # Load recommendation model
            model = ContentRecommendationModel()
            # In production, load from saved model
            # model.load_model('/path/to/recommendation_model.joblib')
            
            # Get recommendations
            recommendations = model.get_recommendations(
                user_tier, platform, recent_performance
            )
            
            return Response({
                'user_tier': user_tier,
                'platform': platform,
                'recommendations': recommendations,
                'recent_performance': recent_performance
            })
            
        except Exception as e:
            logger.error(f'Error getting content recommendations: {str(e)}')
            return Response(
                {'error': 'Failed to get content recommendations'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_recent_performance_by_category(self, user) -> Dict[str, float]:
        """Get user's recent performance by content category"""
        
        from social.models import Post
        
        recent_posts = Post.objects.filter(
            user=user,
            status='published',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).select_related('metrics')
        
        category_performance = {}
        
        for post in recent_posts:
            category = getattr(post, 'content_category', 'General')
            
            if category not in category_performance:
                category_performance[category] = []
            
            engagement = 0
            if hasattr(post, 'metrics') and post.metrics:
                engagement = (post.metrics.likes_count or 0) + \
                           (post.metrics.comments_count or 0) + \
                           (post.metrics.shares_count or 0)
            
            category_performance[category].append(engagement)
        
        # Calculate averages
        avg_performance = {}
        for category, engagements in category_performance.items():
            avg_performance[category] = sum(engagements) / len(engagements) if engagements else 0
        
        return avg_performance
```

## Real-time Analytics Dashboard

### Dashboard Components

```python
# backend/analytics/dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any

@login_required
def analytics_dashboard(request):
    """Render analytics dashboard"""
    return render(request, 'analytics/dashboard.html')

@login_required
def dashboard_data(request):
    """Get real-time dashboard data"""
    
    user = request.user
    
    # Get real-time metrics
    metrics = {
        'overview': _get_overview_metrics(user),
        'content_performance': _get_content_performance_metrics(user),
        'ai_usage': _get_ai_usage_metrics(user),
        'social_growth': _get_social_growth_metrics(user),
        'alerts': _get_user_alerts(user)
    }
    
    return JsonResponse(metrics)

def _get_overview_metrics(user) -> Dict[str, Any]:
    """Get overview metrics for dashboard"""
    
    from social.models import Post, SocialMediaAccount
    from ai.models import AIRequest
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Posts metrics
    total_posts = Post.objects.filter(user=user).count()
    posts_this_week = Post.objects.filter(
        user=user,
        created_at__date__gte=week_ago
    ).count()
    
    # Social accounts
    social_accounts = SocialMediaAccount.objects.filter(user=user).count()
    total_followers = SocialMediaAccount.objects.filter(user=user).aggregate(
        total=models.Sum('followers_count')
    )['total'] or 0
    
    # AI usage
    ai_requests_today = AIRequest.objects.filter(
        user=user,
        created_at__date=today
    ).count()
    
    return {
        'total_posts': total_posts,
        'posts_this_week': posts_this_week,
        'social_accounts': social_accounts,
        'total_followers': total_followers,
        'ai_requests_today': ai_requests_today
    }

def _get_content_performance_metrics(user) -> Dict[str, Any]:
    """Get content performance metrics"""
    
    from social.models import Post
    
    # Get recent posts with metrics
    recent_posts = Post.objects.filter(
        user=user,
        status='published',
        created_at__gte=timezone.now() - timedelta(days=30)
    ).select_related('metrics')
    
    total_engagement = 0
    best_performing_post = None
    best_engagement = 0
    
    for post in recent_posts:
        if hasattr(post, 'metrics') and post.metrics:
            engagement = (post.metrics.likes_count or 0) + \
                        (post.metrics.comments_count or 0) + \
                        (post.metrics.shares_count or 0)
            
            total_engagement += engagement
            
            if engagement > best_engagement:
                best_engagement = engagement
                best_performing_post = {
                    'id': post.id,
                    'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                    'platform': post.platform,
                    'engagement': engagement
                }
    
    avg_engagement = total_engagement / recent_posts.count() if recent_posts.count() > 0 else 0
    
    return {
        'total_engagement': total_engagement,
        'avg_engagement': avg_engagement,
        'best_performing_post': best_performing_post,
        'posts_analyzed': recent_posts.count()
    }

def _get_ai_usage_metrics(user) -> Dict[str, Any]:
    """Get AI usage metrics"""
    
    from ai.models import AIRequest, AIUsageLog
    
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)
    
    # AI requests this month
    ai_requests = AIRequest.objects.filter(
        user=user,
        created_at__date__gte=month_ago
    )
    
    # Usage costs
    usage_logs = AIUsageLog.objects.filter(
        user=user,
        timestamp__date__gte=month_ago
    )
    
    total_cost = sum(log.cost for log in usage_logs)
    total_tokens = sum(log.tokens_used for log in usage_logs)
    
    # Request types breakdown
    request_types = {}
    for request in ai_requests:
        req_type = request.request_type
        request_types[req_type] = request_types.get(req_type, 0) + 1
    
    return {
        'total_requests': ai_requests.count(),
        'total_cost': float(total_cost),
        'total_tokens': total_tokens,
        'request_types': request_types,
        'avg_cost_per_request': float(total_cost / ai_requests.count()) if ai_requests.count() > 0 else 0
    }

def _get_social_growth_metrics(user) -> Dict[str, Any]:
    """Get social media growth metrics"""
    
    from social.models import SocialMediaAccount
    
    accounts = SocialMediaAccount.objects.filter(user=user)
    
    platform_stats = {}
    total_followers = 0
    
    for account in accounts:
        platform_stats[account.platform] = {
            'followers': account.followers_count or 0,
            'following': account.following_count or 0,
            'posts': account.posts_count or 0,
            'engagement_rate': account.engagement_rate or 0
        }
        total_followers += account.followers_count or 0
    
    return {
        'platform_stats': platform_stats,
        'total_followers': total_followers,
        'platforms_connected': len(platform_stats)
    }

def _get_user_alerts(user) -> List[Dict[str, Any]]:
    """Get user alerts and notifications"""
    
    alerts = []
    
    # Check for low engagement
    recent_avg_engagement = _get_recent_avg_engagement(user)
    if recent_avg_engagement < 10:  # Threshold for low engagement
        alerts.append({
            'type': 'warning',
            'title': 'Low Engagement Alert',
            'message': 'Your recent posts have lower than average engagement. Consider trying different content types.',
            'action': 'View Content Recommendations'
        })
    
    # Check for AI usage limits
    ai_usage_percentage = _get_ai_usage_percentage(user)
    if ai_usage_percentage > 80:
        alerts.append({
            'type': 'info',
            'title': 'AI Usage Alert',
            'message': f'You\'ve used {ai_usage_percentage}% of your monthly AI quota.',
            'action': 'Upgrade Plan'
        })
    
    # Check for unconnected social accounts
    from social.models import SocialMediaAccount
    connected_platforms = SocialMediaAccount.objects.filter(user=user).count()
    if connected_platforms == 0:
        alerts.append({
            'type': 'info',
            'title': 'Connect Social Accounts',
            'message': 'Connect your social media accounts to start managing your content.',
            'action': 'Connect Accounts'
        })
    
    return alerts

def _get_recent_avg_engagement(user) -> float:
    """Calculate recent average engagement"""
    
    from social.models import Post
    
    recent_posts = Post.objects.filter(
        user=user,
        status='published',
        created_at__gte=timezone.now() - timedelta(days=7)
    ).select_related('metrics')
    
    if not recent_posts:
        return 0.0
    
    total_engagement = 0
    for post in recent_posts:
        if hasattr(post, 'metrics') and post.metrics:
            engagement = (post.metrics.likes_count or 0) + \
                        (post.metrics.comments_count or 0) + \
                        (post.metrics.shares_count or 0)
            total_engagement += engagement
    
    return total_engagement / recent_posts.count()

def _get_ai_usage_percentage(user) -> float:
    """Get AI usage percentage for current month"""
    
    from ai.models import AIUsageLog
    from billing.models import SubscriptionTier
    
    # Get current month usage
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    current_usage = AIUsageLog.objects.filter(
        user=user,
        timestamp__gte=month_start
    ).aggregate(total_tokens=models.Sum('tokens_used'))['total_tokens'] or 0
    
    # Get user's tier limits
    tier_limits = {
        'free': 1000,
        'starter': 10000,
        'professional': 50000,
        'business': 200000,
        'enterprise': 1000000
    }
    
    user_limit = tier_limits.get(user.subscription_tier, 1000)
    
    return (current_usage / user_limit) * 100 if user_limit > 0 else 0
```

## Team Responsibilities

### Data Science Team

**Primary Responsibilities:**
- Design and implement ETL pipelines for data processing
- Develop machine learning models for engagement prediction, churn analysis, and content optimization
- Create analytics dashboards and reporting systems
- Monitor data quality and model performance
- Conduct A/B testing and statistical analysis

**Key Deliverables:**
- ETL pipeline implementation (`DataPipeline` class)
- ML models for engagement prediction and churn analysis
- Analytics API endpoints for real-time insights
- Dashboard data processing and visualization
- Data quality monitoring and alerting systems

**Technical Skills Required:**
- Python, pandas, scikit-learn, numpy
- SQL and database optimization
- Statistical analysis and A/B testing
- Data visualization (matplotlib, plotly)
- ETL tools and data pipeline design

### Backend Team Integration

**Data Science Dependencies:**
- Django models for data access
- API endpoints for serving analytics
- Database optimization for analytics queries
- Caching strategies for dashboard performance
- Background task processing for ETL jobs

**Collaboration Points:**
- Model serving through Django REST API
- Database schema design for analytics
- Performance optimization for large datasets
- Integration with existing authentication and authorization

### Frontend Team Integration

**Analytics Dashboard Requirements:**
- Real-time data visualization components
- Interactive charts and graphs
- Responsive design for mobile analytics
- Export functionality for reports
- Alert and notification systems

**Key Components to Build:**
- Analytics dashboard pages
- Chart components (line, bar, pie charts)
- Data export functionality
- Real-time updates using WebSockets
- Mobile-responsive analytics views

### Security Team Considerations

**Data Privacy and Security:**
- Anonymization of sensitive user data
- Secure data transmission and storage
- Access control for analytics data
- Compliance with data protection regulations
- Audit logging for data access

**Implementation Requirements:**
- Data encryption at rest and in transit
- Role-based access to analytics features
- Secure API endpoints with proper authentication
- Data retention and deletion policies
- Privacy-preserving analytics techniques

### AI Team Integration

**ML Model Integration:**
- Model serving infrastructure
- Real-time prediction APIs
- Model versioning and deployment
- Performance monitoring and retraining
- Feature engineering collaboration

**Shared Responsibilities:**
- AI usage analytics and cost tracking
- Model performance evaluation
- Feature store management
- A/B testing for AI features
- Continuous model improvement

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
- Set up data pipeline infrastructure
- Implement basic ETL processes
- Create initial database schemas for analytics
- Set up monitoring and logging

### Phase 2: Core Analytics (Weeks 3-4)
- Develop user analytics API endpoints
- Implement basic dashboard data processing
- Create initial ML models for engagement prediction
- Set up real-time data processing

### Phase 3: Advanced Features (Weeks 5-6)
- Implement churn prediction models
- Add content recommendation system
- Create optimal timing analysis
- Develop advanced dashboard features

### Phase 4: Optimization (Weeks 7-8)
- Performance optimization and caching
- Advanced analytics features
- A/B testing framework
- Production deployment and monitoring

## Success Metrics

### Technical Metrics
- ETL pipeline processing time < 30 minutes for daily jobs
- API response time < 200ms for analytics endpoints
- Model prediction accuracy > 80% for engagement prediction
- Dashboard load time < 3 seconds
- Data freshness < 1 hour for real-time metrics

### Business Metrics
- User engagement with analytics features > 60%
- Improvement in content performance through recommendations
- Reduction in churn rate through predictive alerts
- Increase in user satisfaction with data-driven insights
- Cost optimization through AI usage analytics