"""
Helper utilities
"""
from typing import Any, Dict
import json


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Integer value
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def format_currency(amount: float) -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}M"


def format_percentage(value: float) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value to format
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.2f}%"


def validate_json(data: str) -> bool:
    """
    Validate if string is valid JSON
    
    Args:
        data: JSON string to validate
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        json.loads(data)
        return True
    except (ValueError, TypeError):
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename
