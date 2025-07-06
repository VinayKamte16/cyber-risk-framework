import os
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import logging
from typing import Dict, Any, List
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RiskPredictor:
    """Handles risk prediction using the trained model."""
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize the risk predictor.
        Args:
            model_dir: Directory containing trained model files
        """
        self.model_dir = model_dir
        self.model = None
        self.metadata = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load the trained model and metadata."""
        try:
            # Load model
            model_path = os.path.join(self.model_dir, 'risk_model.joblib')
            self.model = joblib.load(model_path)
            
            # Load metadata
            metadata_path = os.path.join(self.model_dir, 'model_metadata.joblib')
            self.metadata = joblib.load(metadata_path)
            
            logger.info("Model and metadata loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def preprocess_event(self, event: Dict[str, Any]) -> pd.DataFrame:
        """
        Preprocess a single security event for prediction.
        Args:
            event: Security event dictionary
        Returns:
            Preprocessed DataFrame
        """
        try:
            # Convert event to DataFrame
            df = pd.DataFrame([event])
            
            # Convert timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            df['day'] = df['timestamp'].dt.day
            df['year'] = df['timestamp'].dt.year
            df = df.drop(columns=['timestamp'])
            
            # Encode severity
            severity_map = {
                'info': 1,
                'warning': 2,
                'error': 3,
                'critical': 4
            }
            df['severity_numeric'] = df['severity'].map(severity_map)
            
            # Handle list-type columns more efficiently
            list_columns = []
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, list)).any():
                    list_columns.append(col)
            
            # Create a new DataFrame for list-type columns
            list_dfs = []
            for col in list_columns:
                # Get max length from training data
                max_len = len([c for c in self.metadata['feature_names'] if c.startswith(f'{col}_')])
                if max_len == 0:
                    continue
                
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
            
            # Ensure all features from training are present and properly encoded
            missing_features = set(self.metadata['feature_names']) - set(df.columns)
            for feature in missing_features:
                if feature == 'Risk Level Prediction':
                    df[feature] = 'High'  # Default value
                elif feature == 'Sentiment in Forums':
                    df[feature] = 'Negative'  # Default value
                else:
                    df[feature] = None
            
            # Reorder columns to match training data
            df = df[self.metadata['feature_names']]
            
            # Encode categorical features
            for col in df.select_dtypes(include=['object']).columns:
                if col in self.metadata['label_encoders']:
                    classes = self.metadata['label_encoders'][col].classes_
                    df[col] = df[col].apply(lambda x: x if x in classes else classes[0])
                    df[col] = self.metadata['label_encoders'][col].transform(df[col].astype(str))
            
            # Convert all columns to numeric
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Scale numerical features
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            df[numerical_cols] = self.metadata['scaler'].transform(df[numerical_cols])
            
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing event: {str(e)}")
            raise
    
    def predict_risk(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict risk score for a security event.
        Args:
            event: Security event dictionary
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Preprocess event
            df_processed = self.preprocess_event(event)
            
            # Make prediction
            base_risk_score = self.model.predict(df_processed)[0]
            
            # Apply severity weighting
            severity_weights = {
                'info': 1.0,
                'warning': 1.5,
                'error': 2.0,
                'critical': 3.0
            }
            severity = event.get('severity', 'info').lower()
            weighted_risk_score = base_risk_score * severity_weights.get(severity, 1.0)
            
            # Cap the score at 100
            weighted_risk_score = min(weighted_risk_score, 100)
            
            # Determine risk level with adjusted thresholds
            if weighted_risk_score >= 80:
                risk_level = "Critical"
            elif weighted_risk_score >= 60:
                risk_level = "High"
            elif weighted_risk_score >= 40:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            result = {
                'event_id': event.get('event_id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'risk_score': float(weighted_risk_score),
                'risk_level': risk_level,
                'base_risk_score': float(base_risk_score),
                'severity_weight': severity_weights.get(severity, 1.0),
                'original_event': event
            }
            
            logger.info(f"Predicted risk score: {weighted_risk_score:.2f} ({risk_level})")
            return result
            
        except Exception as e:
            logger.error(f"Error predicting risk: {str(e)}")
            raise

def main():
    # Example usage
    predictor = RiskPredictor()
    
    # Example security event with all required features
    example_event = {
        'event_id': 'EVT-001',
        'timestamp': '2024-04-15T10:30:00',
        'severity': 'critical',
        'event_type': 'unauthorized_access',
        'source': '192.168.1.100',
        'description': 'Multiple failed login attempts detected',
        'Attack Vector': 'Network',
        'Cleaned Threat Description': 'Unauthorized access attempt from external IP',
        'Geographical Location': 'United States',
        'IOCs (Indicators of Compromise)': ['192.168.1.100', 'admin'],
        'Threat Type': 'Brute Force',
        'Threat Source': 'External',
        'Threat Actor': 'Unknown',
        'Threat Actor Type': 'Script Kiddie',
        'Threat Actor Motivation': 'Financial',
        'Threat Actor Capability': 'Low',
        'Threat Actor Resources': 'Limited',
        'Threat Actor Intent': 'Malicious',
        'Threat Actor TTPs': ['Brute Force', 'Password Spraying'],
        'Threat Actor Tools': ['Hydra', 'Nmap'],
        'Threat Actor Infrastructure': ['VPN', 'Proxy'],
        'Threat Actor Communication': ['Email', 'IRC'],
        'Threat Actor Persistence': ['Backdoor', 'RAT'],
        'Threat Actor Evasion': ['Encryption', 'Obfuscation'],
        'Threat Actor Discovery': ['Network Scanning', 'Port Scanning'],
        'Threat Actor Lateral Movement': ['RDP', 'SSH'],
        'Threat Actor Collection': ['Data Exfiltration', 'Screen Capture'],
        'Threat Actor Command and Control': ['HTTP', 'DNS'],
        'Threat Actor Exfiltration': ['FTP', 'Cloud Storage'],
        'Threat Actor Impact': ['Data Theft', 'System Compromise'],
        'Threat Actor Objectives': ['Financial Gain', 'Data Theft'],
        'Threat Actor Constraints': ['Time', 'Resources'],
        'Threat Actor Preferences': ['Windows', 'Linux'],
        'Threat Actor History': ['Previous Attacks', 'Known TTPs'],
        'Threat Actor Reputation': 'Low',
        'Threat Actor Reliability': 'Low',
        'Threat Actor Confidence': 'Low',
        'Threat Actor Accuracy': 'Low',
        'Threat Actor Timeliness': 'Low',
        'Threat Actor Relevance': 'Low',
        'Threat Actor Completeness': 'Low',
        'Threat Actor Consistency': 'Low',
        'Threat Actor Uniqueness': 'Low',
        'Threat Actor Validity': 'Low',
        'Threat Actor Verifiability': 'Low',
        'Threat Actor Traceability': 'Low',
        'Threat Actor Accountability': 'Low',
        'Threat Actor Responsibility': 'Low',
        'Threat Actor Liability': 'Low',
        'Threat Actor Culpability': 'Low',
        'Threat Actor Blame': 'Low',
        'Threat Actor Fault': 'Low',
        'Threat Actor Error': 'Low',
        'Threat Actor Mistake': 'Low',
        'Threat Actor Negligence': 'Low',
        'Threat Actor Recklessness': 'Low',
        'Threat Actor Intentionality': 'Low',
        'Threat Actor Knowledge': 'Low',
        'Threat Actor Awareness': 'Low',
        'Threat Actor Understanding': 'Low',
        'Threat Actor Recognition': 'Low',
        'Threat Actor Perception': 'Low',
        'Threat Actor Consciousness': 'Low',
        'Threat Actor Attention': 'Low',
        'Threat Actor Focus': 'Low',
        'Threat Actor Concentration': 'Low',
        'Threat Actor Awareness of Consequences': 'Low',
        'Threat Actor Awareness of Risks': 'Low',
        'Threat Actor Awareness of Dangers': 'Low',
        'Threat Actor Awareness of Threats': 'Low',
        'Threat Actor Awareness of Vulnerabilities': 'Low',
        'Threat Actor Awareness of Exploits': 'Low',
        'Threat Actor Awareness of Attacks': 'Low',
        'Threat Actor Awareness of Intrusions': 'Low',
        'Threat Actor Awareness of Breaches': 'Low',
        'Threat Actor Awareness of Compromises': 'Low',
        'Threat Actor Awareness of Incidents': 'Low',
        'Threat Actor Awareness of Events': 'Low',
        'Threat Actor Awareness of Situations': 'Low',
        'Threat Actor Awareness of Circumstances': 'Low',
        'Threat Actor Awareness of Conditions': 'Low',
        'Threat Actor Awareness of States': 'Low',
        'Threat Actor Awareness of Environments': 'Low',
        'Threat Actor Awareness of Contexts': 'Low',
        'Threat Actor Awareness of Scenarios': 'Low',
        'Threat Actor Awareness of Cases': 'Low',
        'Threat Actor Awareness of Examples': 'Low',
        'Threat Actor Awareness of Instances': 'Low',
        'Threat Actor Awareness of Occurrences': 'Low',
        'Threat Actor Awareness of Happenings': 'Low',
        'Threat Actor Awareness of Episodes': 'Low',
        'Keyword Extraction': ['unauthorized', 'access', 'login', 'attempts'],
        'Named Entities (NER)': ['192.168.1.100', 'admin'],
        'Risk Level Prediction': 'High',
        'Sentiment in Forums': 'Negative'
    }
    
    # Make prediction
    result = predictor.predict_risk(example_event)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 