"""
Data preprocessing module for cybersecurity risk scoring framework.
Handles feature engineering, normalization, and data cleaning.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Handles preprocessing of security logs and threat intelligence data."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.tfidf = TfidfVectorizer(max_features=1000)
        self.feature_names = []
        
    def clean_log_data(self, log_data: List[Dict]) -> pd.DataFrame:
        """
        Clean and normalize log data.
        Args:
            log_data: List of log entries
        Returns:
            DataFrame with cleaned log data
        """
        try:
            df = pd.DataFrame(log_data)
            
            # Handle missing values
            df = df.fillna({
                'severity': 'info',
                'source_ip': '0.0.0.0',
                'destination_ip': '0.0.0.0'
            })
            
            # Convert timestamps
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Encode categorical features
            categorical_cols = ['severity', 'event_type']
            for col in categorical_cols:
                if col in df.columns:
                    df = pd.get_dummies(df, columns=[col], prefix=col)
            
            self.feature_names = df.columns.tolist()
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning log data: {str(e)}")
            raise
            
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional features for risk scoring.
        Args:
            df: DataFrame with cleaned log data
        Returns:
            DataFrame with engineered features
        """
        try:
            # Network traffic features
            if 'source_ip' in df.columns and 'destination_ip' in df.columns:
                df['unique_ips'] = df['source_ip'].nunique() + df['destination_ip'].nunique()
                df['ip_entropy'] = df['source_ip'].value_counts().apply(
                    lambda x: -x * np.log2(x)
                ).sum()
            
            # Time-based features
            if 'timestamp' in df.columns:
                df['time_since_last_event'] = df['timestamp'].diff().dt.total_seconds()
                df['events_per_minute'] = df.groupby(
                    df['timestamp'].dt.floor('min')
                )['timestamp'].transform('count')
            
            # Text-based features for log messages
            if 'message' in df.columns:
                tfidf_features = self.tfidf.fit_transform(df['message'])
                tfidf_df = pd.DataFrame(
                    tfidf_features.toarray(),
                    columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])]
                )
                df = pd.concat([df, tfidf_df], axis=1)
            
            return df
            
        except Exception as e:
            logger.error(f"Error engineering features: {str(e)}")
            raise
            
    def normalize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize numerical features.
        Args:
            df: DataFrame with engineered features
        Returns:
            DataFrame with normalized features
        """
        try:
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            df[numerical_cols] = self.scaler.fit_transform(df[numerical_cols])
            return df
            
        except Exception as e:
            logger.error(f"Error normalizing features: {str(e)}")
            raise
            
    def process_data(self, log_data: List[Dict]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Complete preprocessing pipeline.
        Args:
            log_data: Raw log data
        Returns:
            Tuple of (processed DataFrame, feature names)
        """
        try:
            df = self.clean_log_data(log_data)
            df = self.engineer_features(df)
            df = self.normalize_features(df)
            return df, self.feature_names
            
        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            raise 