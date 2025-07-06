"""
Explainable AI module for cybersecurity risk scoring framework.
Implements SHAP and LIME explanations for model interpretability.
"""

import numpy as np
import pandas as pd
import shap
import lime
import lime.lime_tabular
from typing import Dict, List, Optional, Union
import logging
from sklearn.base import BaseEstimator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExplainableAI:
    """Handles model explanations using SHAP and LIME."""
    
    def __init__(self, model: BaseEstimator, feature_names: List[str]):
        """
        Initialize model explainer.
        Args:
            model: Trained ML model
            feature_names: List of feature names
        """
        self.model = model
        self.feature_names = feature_names
        self.shap_explainer = None
        self.lime_explainer = None
        
    def initialize_shap(self, background_data: np.ndarray) -> None:
        """
        Initialize SHAP explainer with background data.
        Args:
            background_data: Background data for SHAP explainer
        """
        try:
            self.shap_explainer = shap.KernelExplainer(
                self.model.predict_proba,
                shap.sample(background_data, 100)
            )
            logger.info("SHAP explainer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing SHAP explainer: {str(e)}")
            raise
            
    def initialize_lime(self, training_data: np.ndarray) -> None:
        """
        Initialize LIME explainer with training data.
        Args:
            training_data: Training data for LIME explainer
        """
        try:
            self.lime_explainer = lime.lime_tabular.LimeTabularExplainer(
                training_data,
                feature_names=self.feature_names,
                class_names=['low_risk', 'high_risk'],
                mode='classification'
            )
            logger.info("LIME explainer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LIME explainer: {str(e)}")
            raise
            
    def explain_shap(self, instance: np.ndarray) -> Dict:
        """
        Generate SHAP explanation for an instance.
        Args:
            instance: Data instance to explain
        Returns:
            Dictionary containing SHAP values and feature importance
        """
        try:
            if self.shap_explainer is None:
                raise ValueError("SHAP explainer not initialized")
                
            shap_values = self.shap_explainer.shap_values(instance)
            
            # Convert to feature importance format
            feature_importance = []
            for i, feature in enumerate(self.feature_names):
                feature_importance.append({
                    'feature': feature,
                    'importance': float(np.abs(shap_values[0][i]))
                })
            
            # Sort by importance
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            return {
                'shap_values': shap_values.tolist(),
                'feature_importance': feature_importance[:10]  # Top 10 features
            }
            
        except Exception as e:
            logger.error(f"Error generating SHAP explanation: {str(e)}")
            raise
            
    def explain_lime(self, instance: np.ndarray) -> Dict:
        """
        Generate LIME explanation for an instance.
        Args:
            instance: Data instance to explain
        Returns:
            Dictionary containing LIME explanation
        """
        try:
            if self.lime_explainer is None:
                raise ValueError("LIME explainer not initialized")
                
            exp = self.lime_explainer.explain_instance(
                instance[0],
                self.model.predict_proba,
                num_features=10
            )
            
            return {
                'explanation': exp.as_list(),
                'prediction': float(self.model.predict_proba(instance)[0][1])
            }
            
        except Exception as e:
            logger.error(f"Error generating LIME explanation: {str(e)}")
            raise
            
    def explain_instance(self, instance: np.ndarray) -> Dict:
        """
        Generate comprehensive explanation using both SHAP and LIME.
        Args:
            instance: Data instance to explain
        Returns:
            Dictionary containing combined explanations
        """
        try:
            explanation = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'explanations': {}
            }
            
            # Get SHAP explanation
            if self.shap_explainer is not None:
                explanation['explanations']['shap'] = self.explain_shap(instance)
            
            # Get LIME explanation
            if self.lime_explainer is not None:
                explanation['explanations']['lime'] = self.explain_lime(instance)
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating comprehensive explanation: {str(e)}")
            raise
            
    def explain_batch(self, instances: np.ndarray) -> List[Dict]:
        """
        Generate explanations for a batch of instances.
        Args:
            instances: Array of data instances
        Returns:
            List of explanation dictionaries
        """
        try:
            explanations = []
            for instance in instances:
                explanations.append(self.explain_instance(instance.reshape(1, -1)))
            return explanations
            
        except Exception as e:
            logger.error(f"Error generating batch explanations: {str(e)}")
            raise 