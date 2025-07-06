import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime, timedelta
import logging
from typing import Tuple, Dict, Any, List
import random
import string
import json
from ast import literal_eval
from sklearn.metrics import mean_squared_error, r2_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatasetTrainer:
    """Handles training of the risk model with custom datasets."""
    
    def __init__(self, dataset_path: str, model_dir: str = "models"):
        """
        Initialize the dataset trainer.
        Args:
            dataset_path: Path to the dataset file
            model_dir: Directory to save trained models
        """
        self.dataset_path = dataset_path
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        self.metadata = {
            'label_encoders': {},
            'feature_names': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Create model directory if it doesn't exist
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
    
    def load_dataset(self) -> pd.DataFrame:
        """
        Load and preprocess the dataset.
        Returns:
            Preprocessed DataFrame
        """
        try:
            # Load dataset based on file extension
            if self.dataset_path.endswith('.csv'):
                df = pd.read_csv(self.dataset_path)
            elif self.dataset_path.endswith('.xlsx'):
                df = pd.read_excel(self.dataset_path)
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel files.")
            
            # Validate required columns
            required_columns = ['timestamp', 'severity', 'event_type']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            raise
    
    def generate_synthetic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate synthetic data for missing required columns.
        Args:
            df: Original DataFrame
        Returns:
            DataFrame with all required columns
        """
        try:
            # Generate source and destination IPs
            df['source'] = df.apply(lambda _: f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}", axis=1)
            df['description'] = df.apply(lambda row: f"{row['event_type']} event with {row['severity']} severity", axis=1)
            
            # Generate details JSON
            df['details'] = df.apply(lambda row: {
                'event_id': ''.join(random.choices(string.ascii_letters + string.digits, k=8)),
                'source_ip': row['source'],
                'destination_ip': f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
                'protocol': random.choice(['TCP', 'UDP', 'HTTP', 'HTTPS']),
                'port': random.randint(1, 65535)
            }, axis=1)
            
            # Add status column
            df['status'] = 'new'
            
            return df
            
        except Exception as e:
            logger.error(f"Error generating synthetic data: {str(e)}")
            raise
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the dataset for training.
        Args:
            df: Input DataFrame
        Returns:
            Preprocessed DataFrame
        """
        try:
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            df['day'] = df['timestamp'].dt.day
            df['year'] = df['timestamp'].dt.year
            df = df.drop(columns=['timestamp'])
            
            # Encode severity first
            severity_map = {
                'info': 1,
                'warning': 2,
                'error': 3,
                'critical': 4
            }
            df['severity_numeric'] = df['severity'].map(severity_map)
            
            # Calculate base risk score based on severity
            severity_scores = {
                'info': 10,
                'warning': 30,
                'error': 60,
                'critical': 90
            }
            df['risk_score'] = df['severity'].map(severity_scores)
            
            # Adjust risk score based on event type
            event_type_weights = {
                'unauthorized_access': 1.5,
                'malware_detection': 1.8,
                'data_exfiltration': 2.0,
                'brute_force': 1.6,
                'phishing': 1.4,
                'ddos': 1.7,
                'sql_injection': 1.9,
                'xss': 1.3,
                'default': 1.0
            }
            df['event_weight'] = df['event_type'].map(lambda x: event_type_weights.get(x, event_type_weights['default']))
            df['risk_score'] = df['risk_score'] * df['event_weight']
            
            # Encode severity with weights for final scoring
            severity_weights = {
                'info': 1.0,
                'warning': 1.5,
                'error': 2.0,
                'critical': 3.0
            }
            df['severity_weight'] = df['severity'].map(severity_weights)
            
            # Apply severity weighting to risk score
            df['weighted_risk_score'] = df['risk_score'] * df['severity_weight']
            df['weighted_risk_score'] = df['weighted_risk_score'].clip(0, 100)  # Cap at 100
            
            # Handle list-type columns
            list_columns = []
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, list)).any():
                    list_columns.append(col)
            
            # Create a new DataFrame for list-type columns
            list_dfs = []
            for col in list_columns:
                # Get max length of lists in this column
                max_len = df[col].apply(lambda x: len(x) if isinstance(x, list) else 0).max()
                
                # Create columns for each list element
                list_data = {f'{col}_{i}': df[col].apply(lambda x: x[i] if isinstance(x, list) and i < len(x) else None)
                            for i in range(max_len)}
                list_df = pd.DataFrame(list_data)
                list_dfs.append(list_df)
            
            # Drop original list columns
            df = df.drop(columns=list_columns)
            
            # Concatenate all DataFrames
            if list_dfs:
                df = pd.concat([df] + list_dfs, axis=1)
            
            # Encode all categorical features
            for col in df.select_dtypes(include=['object']).columns:
                if col not in ['risk_score', 'weighted_risk_score']:
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.metadata['label_encoders'][col] = le
            
            # Scale numerical features
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            numerical_cols = [col for col in numerical_cols if col not in ['risk_score', 'weighted_risk_score']]
            df[numerical_cols] = self.scaler.fit_transform(df[numerical_cols])
            
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            raise
    
    def train_model(self, df: pd.DataFrame) -> None:
        """
        Train the risk prediction model.
        Args:
            df: Preprocessed DataFrame
        """
        try:
            # Split data into features and target
            X = df.drop(columns=['risk_score', 'weighted_risk_score'])
            y = df['weighted_risk_score']  # Use weighted risk score as target
            
            # Split into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train RandomForest model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            self.test_mse = mean_squared_error(y_test, y_pred)
            self.test_r2 = r2_score(y_test, y_pred)
            
            logger.info(f"Model trained successfully")
            logger.info(f"Mean Squared Error: {self.test_mse:.2f}")
            logger.info(f"R² Score: {self.test_r2:.2f}")
            
            # Save feature names
            self.metadata['feature_names'] = list(X.columns)
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def save_model(self, model: Any, feature_names: List[str]) -> None:
        """
        Save the trained model and metadata.
        Args:
            model: Trained model
            feature_names: List of feature names
        """
        try:
            # Save model
            model_path = os.path.join(self.model_dir, 'risk_model.joblib')
            joblib.dump(model, model_path)
            
            # Save metadata
            metadata = {
                'feature_names': feature_names,
                'timestamp': datetime.now().isoformat(),
                'scaler': self.scaler,
                'label_encoders': self.metadata['label_encoders']
            }
            metadata_path = os.path.join(self.model_dir, 'model_metadata.joblib')
            joblib.dump(metadata, metadata_path)
            
            logger.info(f"Model and metadata saved to {self.model_dir}")
            
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def train(self) -> Dict[str, Any]:
        """
        Complete training pipeline.
        Returns:
            Dictionary containing training metrics
        """
        try:
            # Load and preprocess data
            df = self.load_dataset()
            df_processed = self.preprocess_data(df)
            
            # Train model
            self.train_model(df_processed)
            
            # Save model and metadata
            self.save_model(self.model, self.metadata['feature_names'])
            
            # Add test metrics to metadata
            self.metadata.update({
                'test_r2': self.test_r2,
                'test_mse': self.test_mse
            })
            
            return self.metadata
            
        except Exception as e:
            logger.error(f"Error in training pipeline: {str(e)}")
            raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train risk model with security event data')
    parser.add_argument('--dataset', type=str, required=True, help='Path to the dataset file')
    parser.add_argument('--model-dir', type=str, default='models', help='Directory to save trained models')
    
    args = parser.parse_args()
    
    trainer = DatasetTrainer(
        dataset_path=args.dataset,
        model_dir=args.model_dir
    )
    metrics = trainer.train()
    print(f"Training completed with R2 score: {metrics['test_r2']:.2f}") 