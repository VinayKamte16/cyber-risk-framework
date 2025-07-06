"""
Data ingestion module for cybersecurity risk scoring framework.
Handles log collection and threat intelligence API integration.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
import logging
import json
from datetime import datetime
import pandas as pd
import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .database import get_db, SecurityEvent, Vulnerability, ThreatIntelligence, Asset, DatabaseManager
from .config import settings
from .utils import validate_ip, validate_domain, validate_hash
import vt

import requests
from OTXv2 import OTXv2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataSource(ABC):
    """Abstract base class for all data sources."""
    
    @abstractmethod
    def fetch_data(self) -> Dict:
        """Fetch data from the source."""
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """Validate the fetched data."""
        pass

class LogIngester(DataSource):
    """Handles ingestion of system and application logs."""
    
    def __init__(self, log_path: str):
        self.log_path = log_path
        
    def fetch_data(self) -> Dict:
        """
        Fetch and parse log data from the specified path.
        Returns:
            Dict containing parsed log entries
        """
        try:
            if not os.path.exists(self.log_path):
                raise FileNotFoundError(f"Log file not found: {self.log_path}")
                
            log_data = []
            with open(self.log_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        log_data.append(entry)
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping malformed log entry: {line}")
                        
            return {"source": "system_logs", "data": log_data}
            
        except Exception as e:
            logger.error(f"Error fetching log data: {str(e)}")
            return {"source": "system_logs", "data": [], "error": str(e)}
    
    def validate_data(self, data: Dict) -> bool:
        """
        Validate the structure and content of log data.
        Args:
            data: Dictionary containing log entries
        Returns:
            bool indicating if data is valid
        """
        if not isinstance(data, dict):
            return False
        
        required_fields = ["source", "data"]
        return all(field in data for field in required_fields)

class ThreatIntelligence(DataSource):
    """Integration with threat intelligence APIs."""
    
    def __init__(self, api_keys: Dict[str, str]):
        """
        Initialize threat intelligence clients.
        Args:
            api_keys: Dictionary containing API keys for different services
        """
        self.api_keys = api_keys
        self.otx = OTXv2(api_keys.get("otx")) if api_keys.get("otx") else None
        self.vt_client = vt.Client(api_keys.get("virustotal")) if api_keys.get("virustotal") else None
        
    def fetch_data(self) -> Dict:
        """
        Fetch threat intelligence data from multiple sources.
        Returns:
            Dict containing combined threat intelligence data
        """
        threat_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "sources": {}
        }
        
        # Fetch OTX data
        if self.otx:
            try:
                pulses = self.otx.get_pulses(modified_since=datetime.now().strftime("%Y-%m-%d"))
                threat_data["sources"]["otx"] = {
                    "status": "success",
                    "data": pulses
                }
            except Exception as e:
                logger.error(f"Error fetching OTX data: {str(e)}")
                threat_data["sources"]["otx"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Fetch VirusTotal data
        if self.vt_client:
            try:
                # Example: Get information about a domain
                domain_info = self.vt_client.get_object("/domains/example.com")
                threat_data["sources"]["virustotal"] = {
                    "status": "success",
                    "data": domain_info.to_dict()
                }
            except Exception as e:
                logger.error(f"Error fetching VirusTotal data: {str(e)}")
                threat_data["sources"]["virustotal"] = {
                    "status": "error",
                    "error": str(e)
                }
            finally:
                if self.vt_client:
                    self.vt_client.close()
        
        return threat_data
    
    def validate_data(self, data: Dict) -> bool:
        """
        Validate threat intelligence data structure.
        Args:
            data: Dictionary containing threat intelligence data
        Returns:
            bool indicating if data is valid
        """
        if not isinstance(data, dict):
            return False
            
        required_fields = ["timestamp", "sources"]
        if not all(field in data for field in required_fields):
            return False
            
        return True

class DataIngestionManager:
    """Manages all data ingestion sources and processes."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the data ingestion manager."""
        self.config = config
        self.logger = self._setup_logger()
        self.db = DatabaseManager()
        self.vt_client = vt.Client(settings.VIRUSTOTAL_API_KEY)
        self.otx_client = OTXv2(settings.OTX_API_KEY)
        
    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger("data_ingestion")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_file = settings.LOG_FILE or "logs/app.log"
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def collect_all_data(self) -> Dict:
        """
        Collect data from all configured sources.
        Returns:
            Dict containing combined data from all sources
        """
        combined_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": {}
        }
        
        for source_name, source in self.sources.items():
            try:
                data = source.fetch_data()
                if source.validate_data(data):
                    combined_data["data"][source_name] = data
                else:
                    logger.error(f"Invalid data from source: {source_name}")
                    combined_data["data"][source_name] = {"error": "Invalid data format"}
            except Exception as e:
                logger.error(f"Error collecting data from {source_name}: {str(e)}")
                combined_data["data"][source_name] = {"error": str(e)}
        
        return combined_data 