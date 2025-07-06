"""
Risk scoring model module for cybersecurity risk assessment.
Implements multiple ML algorithms for anomaly detection and risk scoring.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support
from typing import Dict, List, Tuple, Optional
import logging
import joblib
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RiskModel:
    """Implements multiple ML models for cybersecurity risk assessment."""
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize risk scoring model.
        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self.isolation_forest = IsolationForest(
            n_estimators=100,
            contamination=0.1,
            random_state=42
        )
        self.one_class_svm = OneClassSVM(
            nu=0.1,
            kernel='rbf',
            gamma='scale'
        )
        self.decision_tree = DecisionTreeClassifier(
            max_depth=10,
            random_state=42
        )
        
        self.models = {
            'isolation_forest': self.isolation_forest,
            'one_class_svm': self.one_class_svm,
            'decision_tree': self.decision_tree
        }
        
    def train(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> Dict:
        """
        Train all models on the provided data.
        Args:
            X: Features DataFrame
            y: Optional labels for supervised learning
        Returns:
            Dictionary containing training metrics
        """
        try:
            metrics = {}
            
            # Split data if labels are provided
            if y is not None:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
            else:
                X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
            
            # Train each model
            for name, model in self.models.items():
                logger.info(f"Training {name}...")
                
                if name == 'decision_tree' and y is not None:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    metrics[name] = precision_recall_fscore_support(
                        y_test, y_pred, average='weighted'
                    )
                else:
                    model.fit(X_train)
                    # For unsupervised models, we use the decision function
                    scores = model.decision_function(X_test)
                    metrics[name] = {
                        'mean_score': np.mean(scores),
                        'std_score': np.std(scores)
                    }
                
                # Save trained model
                model_path = os.path.join(self.model_dir, f"{name}.joblib")
                joblib.dump(model, model_path)
                logger.info(f"Saved {name} to {model_path}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            raise
            
    def predict_risk(self, X: pd.DataFrame) -> Dict:
        """
        Predict risk scores using all models.
        Args:
            X: Features DataFrame
        Returns:
            Dictionary containing risk scores from each model
        """
        try:
            scores = {}
            
            for name, model in self.models.items():
                if name == 'decision_tree':
                    # For decision tree, use predict_proba if available
                    if hasattr(model, 'predict_proba'):
                        scores[name] = model.predict_proba(X)[:, 1]
                    else:
                        scores[name] = model.predict(X)
                else:
                    # For anomaly detection models, use decision function
                    scores[name] = model.decision_function(X)
            
            # Combine scores using weighted average
            combined_score = np.mean(list(scores.values()), axis=0)
            
            return {
                'individual_scores': scores,
                'combined_score': combined_score,
                'risk_level': self._map_to_risk_level(combined_score)
            }
            
        except Exception as e:
            logger.error(f"Error predicting risk: {str(e)}")
            raise
            
    def _map_to_risk_level(self, scores: np.ndarray) -> List[str]:
        """
        Map numerical scores to risk levels.
        Args:
            scores: Array of risk scores
        Returns:
            List of risk levels
        """
        risk_levels = []
        for score in scores:
            if score < -0.5:
                risk_levels.append('CRITICAL')
            elif score < 0:
                risk_levels.append('HIGH')
            elif score < 0.5:
                risk_levels.append('MEDIUM')
            else:
                risk_levels.append('LOW')
        return risk_levels
        
    def load_models(self) -> None:
        """Load trained models from disk."""
        try:
            for name in self.models.keys():
                model_path = os.path.join(self.model_dir, f"{name}.joblib")
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
                    logger.info(f"Loaded {name} from {model_path}")
                else:
                    logger.warning(f"No saved model found for {name}")
                    
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise 