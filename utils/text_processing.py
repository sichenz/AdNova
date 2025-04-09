"""
Text processing utilities for the Marketing Ad Agent.
This module provides helper functions for text manipulation and analysis.
"""
from typing import List, Dict, Any, Optional, Tuple

from config.settings import DEFAULT_MODEL, ANALYTICAL_TEMPERATURE
from utils.api_utils import get_openai_client

def summarize_text(text: str, max_length: int = 100) -> str:
    """
    Summarize a long text to a shorter length.
    
    Args:
        text: The text to summarize
        max_length: Maximum length of the summary in words
        
    Returns:
        Summarized text
    """
    # If the text is already short enough, return it as is
    if len(text.split()) <= max_length:
        return text
    
    client = get_openai_client()
    
    prompt = f"""
    Summarize the following text in {max_length} words or less:
    
    {text}
    
    Ensure the summary captures the key points and maintains the original tone.
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are a skilled summarizer that preserves meaning while condensing text."},
            {"role": "user", "content": prompt}
        ],
        temperature=ANALYTICAL_TEMPERATURE,
        max_tokens=max_length * 4  # Allow enough tokens for the summary
    )
    
    return response.choices[0].message.content.strip()

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract important keywords from a text.
    
    Args:
        text: The text to analyze
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        List of keywords
    """
    client = get_openai_client()
    
    prompt = f"""
    Extract the {max_keywords} most important keywords or phrases from the following text:
    
    {text}
    
    Return only the keywords, one per line, with no numbering or additional text.
    Focus on terms that are most relevant to marketing and user intent.
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are a precise keyword extraction tool that identifies the most important marketing-relevant terms."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=max_keywords * 5  # Allow enough tokens for the keywords
    )
    
    # Parse the response
    keywords_text = response.choices[0].message.content.strip()
    keywords = [k.strip() for k in keywords_text.split("\n") if k.strip()]
    
    return keywords[:max_keywords]

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of a text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary containing sentiment analysis results
    """
    client = get_openai_client()
    
    prompt = f"""
    Analyze the sentiment of the following text:
    
    {text}
    
    Provide a detailed analysis including:
    1. Overall sentiment (positive, negative, neutral, or mixed)
    2. Confidence level (high, medium, low)
    3. Key emotional tones detected
    4. Any notable sentiment shifts
    
    Format the response as a JSON object with these fields.
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are a sentiment analysis expert with nuanced understanding of emotion in text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=300
    )
    
    # Parse the response
    import json
    
    analysis_text = response.choices[0].message.content.strip()
    
    try:
        # Try to parse as JSON
        if "```json" in analysis_text:
            analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
        elif "```" in analysis_text:
            analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
        sentiment_analysis = json.loads(analysis_text)
    except (json.JSONDecodeError, IndexError):
        # Fall back to a basic structure if parsing fails
        sentiment_analysis = {
            "overall_sentiment": "neutral",
            "confidence_level": "medium",
            "emotional_tones": ["not determined"],
            "sentiment_shifts": False,
            "parsing_error": True
        }
    
    return sentiment_analysis

def compare_texts(text1: str, text2: str) -> Dict[str, Any]:
    """
    Compare two texts and identify similarities and differences.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Dictionary containing comparison results
    """
    client = get_openai_client()
    
    prompt = f"""
    Compare the following two texts and identify key similarities and differences:
    
    TEXT 1:
    {text1}
    
    TEXT 2:
    {text2}
    
    Provide an analysis that includes:
    1. Key similarities in content, tone, structure, and messaging
    2. Key differences in content, tone, structure, and messaging
    3. An assessment of which text is likely to be more effective for marketing purposes and why
    
    Format the response as a structured JSON object with these three sections.
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert at comparing and analyzing marketing text."},
            {"role": "user", "content": prompt}
        ],
        temperature=ANALYTICAL_TEMPERATURE,
        max_tokens=800
    )
    
    # Parse the response
    import json
    
    analysis_text = response.choices[0].message.content.strip()
    
    try:
        # Try to parse as JSON
        if "```json" in analysis_text:
            analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
        elif "```" in analysis_text:
            analysis_text = analysis_text.split("```")[1].split("```")[0].strip()
            
        comparison = json.loads(analysis_text)
    except (json.JSONDecodeError, IndexError):
        # Fall back to a basic structure if parsing fails
        comparison = {
            "similarities": ["Could not parse similarities"],
            "differences": ["Could not parse differences"],
            "effectiveness_assessment": "Could not determine which text is more effective",
            "parsing_error": True
        }
    
    return comparison

def format_text_for_platform(text: str, platform: str, max_length: Optional[int] = None) -> str:
    """
    Format text for a specific platform, respecting character limits and conventions.
    
    Args:
        text: The text to format
        platform: Target platform (twitter, facebook, instagram, linkedin, etc.)
        max_length: Optional maximum length override
        
    Returns:
        Formatted text
    """
    # Define platform-specific constraints
    platform_constraints = {
        "twitter": {"max_length": 280, "hashtags": True},
        "x": {"max_length": 280, "hashtags": True},
        "facebook": {"max_length": 5000, "hashtags": False},
        "instagram": {"max_length": 2200, "hashtags": True},
        "linkedin": {"max_length": 3000, "hashtags": False},
        "email_subject": {"max_length": 60, "hashtags": False},
        "meta_description": {"max_length": 155, "hashtags": False},
        "tiktok": {"max_length": 2200, "hashtags": True},
    }
    
    # Get the constraints for the specified platform
    platform = platform.lower()
    if platform not in platform_constraints:
        # Default constraints
        constraints = {"max_length": 1000, "hashtags": False}
    else:
        constraints = platform_constraints[platform]
    
    # Override max_length if specified
    if max_length is not None:
        constraints["max_length"] = max_length
    
    client = get_openai_client()
    
    prompt = f"""
    Format the following text for {platform}, respecting a maximum length of {constraints['max_length']} characters{'and including appropriate hashtags' if constraints['hashtags'] else ''}:
    
    {text}
    
    If the text needs to be shortened, maintain the core message and call-to-action.
    Format the response to be ready for direct posting on {platform}.
    """
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": f"You are an expert {platform} copywriter who formats text optimally for the platform."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=constraints["max_length"] * 2  # Allow enough tokens for the formatted text
    )
    
    formatted_text = response.choices[0].message.content.strip()
    
    # Ensure the text respects the length constraint
    if len(formatted_text) > constraints["max_length"]:
        # Truncate and add ellipsis
        formatted_text = formatted_text[:constraints["max_length"]-3] + "..."
    
    return formatted_text