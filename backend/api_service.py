"""
FastAPI service for cybersecurity risk scoring framework.
Provides endpoints for risk assessment and model management.
"""

import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import logging
import uvicorn
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import random

from models.database import get_db, SecurityEvent, Vulnerability, ThreatIntelligence, Asset
from models.config import settings

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cybersecurity Risk Scoring API",
    description="API for real-time cybersecurity risk assessment",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

security = HTTPBearer()

class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment."""
    log_data: List[Dict] = Field(..., description="Security log entries")
    include_explanation: bool = Field(False, description="Whether to include model explanations")

class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment."""
    timestamp: str
    risk_scores: Dict
    explanations: Optional[Dict] = None
    risk_level: str

class ModelTrainingRequest(BaseModel):
    """Request model for model training."""
    training_data: List[Dict]
    labels: Optional[List[int]] = None

class ModelTrainingResponse(BaseModel):
    """Response model for model training."""
    status: str
    metrics: Dict
    timestamp: str

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify API token."""
    secret_key = os.getenv("SECRET_KEY", "demo_secret_key")
    if credentials.credentials != secret_key:
        raise HTTPException(status_code=403, detail="Invalid token")
    return credentials.credentials

def generate_mock_risk_score():
    """Generate a mock risk score for demonstration."""
    return {
        'risk_score': round(random.uniform(0, 100), 2),
        'confidence': round(random.uniform(0.7, 0.95), 2),
        'risk_level': random.choice(['Low', 'Medium', 'High', 'Critical'])
    }

@app.post("/assess-risk", response_model=RiskAssessmentResponse)
async def assess_risk(
    request: RiskAssessmentRequest,
    token: str = Depends(verify_token)
):
    """
    Assess risk for provided log data using mock data.
    """
    try:
        if not request.log_data:
            raise HTTPException(status_code=400, detail="No log data provided")
            
        # Generate mock risk scores
        risk_scores = {
            'overall': generate_mock_risk_score(),
            'categories': {
                'network': generate_mock_risk_score(),
                'system': generate_mock_risk_score(),
                'application': generate_mock_risk_score()
            }
        }
        
        # Generate mock explanations if requested
        explanations = None
        if request.include_explanation:
            explanations = {
                'top_factors': [
                    {'factor': 'Suspicious IP activity', 'impact': 0.35},
                    {'factor': 'Unusual login attempts', 'impact': 0.25},
                    {'factor': 'System vulnerability', 'impact': 0.20}
                ]
            }
        
        return RiskAssessmentResponse(
            timestamp=datetime.utcnow().isoformat(),
            risk_scores=risk_scores,
            explanations=explanations,
            risk_level=risk_scores['overall']['risk_level']
        )
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train-model", response_model=ModelTrainingResponse)
async def train_model(
    request: ModelTrainingRequest,
    token: str = Depends(verify_token)
):
    """
    Mock model training endpoint.
    """
    try:
        if not request.training_data:
            raise HTTPException(status_code=400, detail="No training data provided")
            
        # Generate mock training metrics
        metrics = {
            'accuracy': round(random.uniform(0.85, 0.95), 3),
            'precision': round(random.uniform(0.80, 0.90), 3),
            'recall': round(random.uniform(0.80, 0.90), 3),
            'f1_score': round(random.uniform(0.80, 0.90), 3)
        }
        
        return ModelTrainingResponse(
            status="success",
            metrics=metrics,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in model training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "api": "operational",
            "database": "operational",
            "cache": "operational"
        }
    }

@app.get("/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get mock dashboard data."""
    return {
        "risk_summary": {
            "total_assets": 150,
            "high_risk_assets": 5,
            "medium_risk_assets": 12,
            "low_risk_assets": 133
        },
        "recent_events": [
            {
                "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "event_type": random.choice(["Login Attempt", "File Access", "System Change"]),
                "severity": random.choice(["Low", "Medium", "High"]),
                "description": f"Mock security event {i+1}"
            }
            for i in range(10)
        ],
        "risk_trends": {
            "daily": [random.randint(0, 100) for _ in range(7)],
            "weekly": [random.randint(0, 100) for _ in range(4)]
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 