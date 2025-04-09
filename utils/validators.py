"""
Validation utilities for the Marketing Ad Agent.
This module provides functions for validating user inputs.
"""
from typing import Dict, Any, List, Optional, Tuple, Union
import re

from config.settings import TONE_OPTIONS, AUDIENCE_SEGMENTS, CAMPAIGN_TYPES

def validate_campaign_brief(brief: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate a campaign brief for required fields and valid values.
    
    Args:
        brief: The campaign brief to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    required_fields = ["product_name", "description", "target_audience", "campaign_goals"]
    for field in required_fields:
        if field not in brief or not brief[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate tone if provided
    if "tone" in brief and brief["tone"] and brief["tone"] not in TONE_OPTIONS:
        errors.append(f"Invalid tone: {brief['tone']}. Valid options: {', '.join(TONE_OPTIONS)}")
    
    # Validate length constraints
    if "description" in brief and len(brief["description"]) > 2000:
        errors.append("Description is too long (maximum 2000 characters)")
    
    if "target_audience" in brief and len(brief["target_audience"]) > 1000:
        errors.append("Target audience description is too long (maximum 1000 characters)")
    
    if "campaign_goals" in brief and len(brief["campaign_goals"]) > 1000:
        errors.append("Campaign goals description is too long (maximum 1000 characters)")
    
    # Check if there are any errors
    is_valid = len(errors) == 0
    
    return is_valid, errors

def validate_ad_request(ad_request: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate an ad generation request.
    
    Args:
        ad_request: The ad generation request
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    if "brief_id" not in ad_request or not ad_request["brief_id"]:
        errors.append("Missing required field: brief_id")
    
    # Validate ad_type if provided
    valid_ad_types = [
        "social_media_post", "headline", "email_subject", "banner_copy",
        "product_description", "landing_page", "video_script", "radio_ad",
        "press_release", "blog_post"
    ]
    
    if "ad_type" in ad_request:
        if ad_request["ad_type"] not in valid_ad_types:
            errors.append(f"Invalid ad_type: {ad_request['ad_type']}. Valid options: {', '.join(valid_ad_types)}")
    
    # Validate variations if provided
    if "variations" in ad_request:
        try:
            variations = int(ad_request["variations"])
            if variations < 1 or variations > 10:
                errors.append("Number of variations must be between 1 and 10")
        except (ValueError, TypeError):
            errors.append("Variations must be a valid number")
    
    # Check if there are any errors
    is_valid = len(errors) == 0
    
    return is_valid, errors

def validate_feedback(feedback: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate client feedback.
    
    Args:
        feedback: The feedback data
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check required fields
    if "ad_id" not in feedback or not feedback["ad_id"]:
        errors.append("Missing required field: ad_id")
    
    if "feedback" not in feedback or not feedback["feedback"]:
        errors.append("Missing required field: feedback")
    
    # Validate score if provided
    if "score" in feedback and feedback["score"] is not None:
        try:
            score = int(feedback["score"])
            if score < 1 or score > 10:
                errors.append("Score must be between 1 and 10")
        except (ValueError, TypeError):
            errors.append("Score must be a valid number")
    
    # Check if there are any errors
    is_valid = len(errors) == 0
    
    return is_valid, errors

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent security issues.
    
    Args:
        text: The text to sanitize
        
    Returns:
        Sanitized text
    """
    # Remove any potentially dangerous HTML or script tags
    text = re.sub(r'<[^>]*script', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]*style', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]*iframe', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]*object', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]*embed', '', text, flags=re.IGNORECASE)
    
    # Replace special characters with their HTML entities
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    
    return text

def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Simple regex pattern for basic email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """
    Validate a URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Regex pattern for URL validation
    pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
    return bool(re.match(pattern, url))

def validate_phone(phone: str) -> bool:
    """
    Validate a phone number.
    
    Args:
        phone: The phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if the resulting string has a valid number of digits (7-15)
    return 7 <= len(digits_only) <= 15