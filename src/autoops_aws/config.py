"""
Configuration Module

This module contains default configuration settings for the AutoOps AWS agent.
"""

from typing import Dict, Any
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"
MODELS_DIR = BASE_DIR / "models"
CACHE_DIR = BASE_DIR / "cache"

# AWS Configuration
DEFAULT_AWS_CONFIG = {
    "region": "us-west-2",
    "max_retries": 3,
    "timeout": 300,
}

# Security Configuration
SECURITY_CONFIG = {
    "allowed_services": [
        "ec2",
        "s3",
        "lambda",
        "cloudwatch",
        "iam",
        "dynamodb",
    ],
    "max_execution_time": 600,  # seconds
    "max_memory_usage": 1024,  # MB
}

# AI/ML Configuration
ML_CONFIG = {
    "model_type": "transformer",
    "max_sequence_length": 512,
    "temperature": 0.7,
    "top_p": 0.9,
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": True
        },
    },
}

def load_config(config_path: Path = None) -> Dict[str, Any]:
    """
    Load configuration from file or return defaults.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Dict containing configuration settings
    """
    if config_path and config_path.exists():
        # TODO: Implement config file loading
        pass
    
    return {
        "aws": DEFAULT_AWS_CONFIG,
        "security": SECURITY_CONFIG,
        "ml": ML_CONFIG,
        "logging": LOGGING_CONFIG,
    } 