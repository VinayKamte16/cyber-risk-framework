"""
FastAPI service for cybersecurity risk scoring framework.
"""

from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import logging
import json
import os
from pathlib import Path

from models.data_ingestion import DataIngestionManager
from models.risk_model import RiskScorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "config.json"
with open(config_path) as f:
    CONFIG = json.load(f)

# Initialize security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize FastAPI app
app = FastAPI(
    title="Cybersecurity Risk Scoring API",
    description="AI-driven cybersecurity risk assessment API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
data_manager = DataIngestionManager(CONFIG.get("data_ingestion", {}))
risk_scorer = RiskScorer(CONFIG.get("risk_scoring", {}))

# Pydantic models for request/response
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class RiskScoreRequest(BaseModel):
    features: Dict[str, float]
    context: Optional[Dict] = None

class RiskScoreResponse(BaseModel):
    request_id: str
    timestamp: str
    scores: Dict[str, float]
    explanations: Optional[Dict] = None
    metadata: Optional[Dict] = None

# Security functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        CONFIG["security"]["secret_key"],
        algorithm=CONFIG["security"]["algorithm"]
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Validate JWT token and return user."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            CONFIG["security"]["secret_key"],
            algorithms=[CONFIG["security"]["algorithm"]]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = User(username=username)
    except jwt.JWTError:
        raise credentials_exception
    return user

# API endpoints
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token."""
    # In production, replace with proper user authentication
    if form_data.username != "admin" or not pwd_context.verify(
        form_data.password, CONFIG["security"]["admin_password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/risk/score", response_model=RiskScoreResponse)
async def get_risk_score(
    request: RiskScoreRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate risk score for input features.
    """
    try:
        # Convert features to DataFrame
        sample = pd.DataFrame([request.features])
        
        # Get risk score
        result = risk_scorer.score_sample(sample)
        
        # Add metadata
        response = {
            "request_id": f"req_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": result["timestamp"],
            "scores": result["scores"],
            "explanations": result["explanations"],
            "metadata": {
                "user": current_user.username,
                "context": request.context
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating risk score: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating risk score: {str(e)}"
        )

@app.post("/api/v1/data/ingest")
async def ingest_data(
    current_user: User = Depends(get_current_user)
):
    """
    Trigger data ingestion from configured sources.
    """
    try:
        data = await data_manager.collect_all_data()
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "data_sources": list(data["data"].keys())
        }
    except Exception as e:
        logger.error(f"Error during data ingestion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during data ingestion: {str(e)}"
        )

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_service:app",
        host=CONFIG.get("server", {}).get("host", "0.0.0.0"),
        port=CONFIG.get("server", {}).get("port", 8000),
        reload=True
    ) 